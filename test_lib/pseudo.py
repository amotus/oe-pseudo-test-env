import os
import shutil
import logging
from dataclasses import dataclass
from pathlib import Path
from contextlib import contextmanager
from subprocess import (PIPE, CalledProcessError, CompletedProcess,
                        TimeoutExpired, Popen)
from typing import Mapping, Optional, Iterator, Iterable
from concurrent.futures import ThreadPoolExecutor

LOGGER = logging.getLogger(__name__)


class PseudoError(Exception):
    pass


class PseudoContextError(PseudoError):
    pass


class PseudoProcessError(PseudoError):
    pass


class PseudoInstallError(PseudoProcessError):
    pass


class PseudoTimeoutError(PseudoProcessError):
    pass


class PseudoCheckError(PseudoError):
    pass


class PseudoNonEmptyStdOutError(PseudoCheckError):
    pass


class PseudoNonEmptyStdErrError(PseudoCheckError):
    pass


def _mk_pseudo_ignore_paths(
    state_dir: Path,
    rootfs_dir: Path
) -> str:
    ignore_paths = [
        "/usr/",
        "/etc/",
        "/lib",
        "/dev/",
        # Our work dir is in temp dir which itself
        # is under `/run`. We Clearly do not want
        # to ignore our work dir.
        # "/run/",
        str(state_dir)
    ]

    return ",".join(ignore_paths)


def _mk_pseudo_env_d(
        pseudo_cmd: str,
        enabled: bool,
        tmp_dir: Optional[Path],
        state_dir: Optional[Path],
        rootfs_dir: Optional[Path]
) -> Mapping[str, str]:
    # Simulate pseudo 'FAKEROOTENV' + 'FAKEROOTBASEENV' env as established
    # by 'poky/meta/conf/bitbake.conf'.
    #
    # In case you change something here, think about making the
    # same change in `./contrib/pseudo-test-env.sh`.
    #
    if tmp_dir is None:
        raise PseudoContextError(
            "Missing *tmp dir*."
        )

    if state_dir is None:
        state_dir = tmp_dir.joinpath("pseudo_state")
        state_dir.mkdir(parents=True)

    if rootfs_dir is None:
        rootfs_dir = tmp_dir.joinpath("pseudo_rootfs")
        rootfs_dir.mkdir(parents=True)

    found_cmd = shutil.which(pseudo_cmd)
    if found_cmd is None:
        raise PseudoInstallError(
            f"Pseudo executable '{pseudo_cmd}' cannot be found.")

    cmd_path = Path(found_cmd)
    bin_dir = cmd_path.parent
    prefix_dir = bin_dir.parent
    lib_dir = prefix_dir.joinpath("lib/pseudo/lib")

    ignore_paths = _mk_pseudo_ignore_paths(
        state_dir=state_dir, rootfs_dir=rootfs_dir)

    return {
        "PSEUDO_BINDIR": str(bin_dir),
        "PSEUDO_PREFIX": str(prefix_dir),
        "PSEUDO_LIBDIR": str(lib_dir),
        "PSEUDO_IGNORE_PATHS": ignore_paths,
        "PSEUDO_DISABLED": "0" if enabled else "1",
        "PSEUDO_LOCALSTATEDIR": str(state_dir),
        "PSEUDO_PASSWD": str(rootfs_dir),
        "PSEUDO_NOSYMLINKEXP": "1",
        # Not sure relevant.
        # PYTHONDONTWRITEBYTECODE: 1,
        #
        #
        # Intended for our test case scripts.
        #
        "IMAGE_ROOTFS": str(rootfs_dir),
        # We capture the provided test temp dir.
        "TMP": str(tmp_dir),
        "TEMP": str(tmp_dir),
        "TEMPDIR": str(tmp_dir),
        "TMPDIR": str(tmp_dir),
        "XDG_RUNTIME_DIR": str(tmp_dir),
    }


@contextmanager
def _popen_pseudo(
        *pseudo_args: str,
        enabled: bool = True,
        state_dir: Optional[Path],
        rootfs_dir: Optional[Path],
        tmp_dir: Optional[Path]
) -> Iterator[Popen]:
    pseudo_cmd = "pseudo"
    fakerootenv_d = _mk_pseudo_env_d(
        pseudo_cmd=pseudo_cmd,
        enabled=enabled,
        tmp_dir=tmp_dir,
        state_dir=state_dir,
        rootfs_dir=rootfs_dir
    )

    val = fakerootenv_d["PSEUDO_IGNORE_PATHS"]
    LOGGER.info(f"'PSEUDO_IGNORE_PATHS={val}'")

    newenv = dict(os.environ)
    newenv.update(fakerootenv_d)

    whole_cmd_w_args = [pseudo_cmd]
    whole_cmd_w_args.extend(
        pseudo_args
    )

    try:
        with Popen(
            whole_cmd_w_args,
            universal_newlines=True,
            env=newenv,
            stdout=PIPE,
            stderr=PIPE,
        ) as process:
            yield process
    except (FileNotFoundError, PermissionError) as e:
        raise PseudoInstallError(
            f"Pseudo executable '{pseudo_cmd}' cannot be found."
        ) from e


def _process_pseudo_outcome(
    process: Popen,
    check_return_code_in: Optional[Iterable[int]],
    check_for_empty_stderr: bool,
    check_for_empty_stdout: bool,
    timeout_s: Optional[float],
) -> CompletedProcess:
    if timeout_s is None:
        timeout_s = 3.0

    whole_cmd_w_args_str = " ".join(str(a) for a in process.args)
    try:
        stdout, stderr = process.communicate(None, timeout=timeout_s)
    except CalledProcessError as e:
        raise PseudoProcessError(
            f"'{whole_cmd_w_args_str}' failed with error "
            f"code '{e.returncode}'. Process stderr: ''\n{e.stderr}''"
        ) from e
    except TimeoutExpired as e:
        process.kill()
        process.wait()
        raise PseudoTimeoutError(
            f"'{whole_cmd_w_args_str}' timeouted after '{e.timeout}' seconds."
        ) from e
    except:  # Including KeyboardInterrupt, communicate handled that.  # noqa
        process.kill()
        # We don't call process.wait() as .__exit__ does that for us.
        raise  # re-rsaise.

    retcode = process.poll()
    assert retcode is not None
    if (check_return_code_in is not None
            and retcode not in check_return_code_in):
        check_return_code_in_str = ", ".join(
            str(ec) for ec in check_return_code_in)
        raise PseudoProcessError(
            f"'{whole_cmd_w_args_str}' failed with unexpected error "
            f"code '{retcode}'. Expected one of the following error "
            f"code: {{{check_return_code_in_str}}}. "
            f"Process stderr: ''\n{stderr}''"
        )

    if check_for_empty_stderr and stderr:
        raise PseudoNonEmptyStdErrError(
            f"'{whole_cmd_w_args_str}' with unexpected non "
            f"empty stderr of: ''\n{stderr}''"
        )

    if check_for_empty_stdout and stdout:
        raise PseudoNonEmptyStdOutError(
            f"'{whole_cmd_w_args_str}' with unexpected non empty "
            f"stdout of: ''\n{stdout}''"
        )

    return CompletedProcess(process.args, retcode, stdout, stderr)


def run_pseudo_client(
        cmd: Path,
        *cmd_args: str,
        enabled: bool = True,
        state_dir: Optional[Path] = None,
        rootfs_dir: Optional[Path] = None,
        tmp_dir: Optional[Path] = None,
        check_for_empty_stderr: bool = False,
        check_for_empty_stdout: bool = False,
        timeout_s: Optional[float] = None
) -> CompletedProcess:
    if timeout_s is None:
        timeout_s = 3.0

    with _popen_pseudo(
        str(cmd), *cmd_args,
        enabled=enabled,
        state_dir=state_dir,
        rootfs_dir=rootfs_dir,
        tmp_dir=tmp_dir
    ) as process:
        return _process_pseudo_outcome(
            process,
            check_return_code_in=[0],
            check_for_empty_stderr=check_for_empty_stderr,
            check_for_empty_stdout=check_for_empty_stdout,
            timeout_s=timeout_s
        )


@dataclass
class PseudoOutcome:
    client: CompletedProcess
    server: CompletedProcess


def run_pseudo(
    cmd: Path, *cmd_args: str,
    enabled: bool = True,
    state_dir: Optional[Path] = None,
    rootfs_dir: Optional[Path] = None,
    tmp_dir: Optional[Path] = None,
    check_for_client_empty_stderr: bool = False,
    check_for_client_empty_stdout: bool = False,
    check_for_server_empty_stderr: bool = False,
    check_for_server_empty_stdout: bool = False,
    client_timeout_s: Optional[float] = None,
    server_timeout_s: Optional[float] = None
) -> PseudoOutcome:
    if server_timeout_s is None:
        server_timeout_s = 3.0

    with _popen_pseudo(
        "-f",
        enabled=enabled,
        state_dir=state_dir,
        rootfs_dir=rootfs_dir,
        tmp_dir=tmp_dir,
    ) as server_process:
        def run_server() -> CompletedProcess:
            return _process_pseudo_outcome(
                server_process,
                check_return_code_in=[0, -15],
                check_for_empty_stderr=check_for_server_empty_stderr,
                check_for_empty_stdout=check_for_server_empty_stdout,
                timeout_s=server_timeout_s
            )

        tpool = ThreadPoolExecutor(max_workers=1)
        future_server_outcome = tpool.submit(run_server)
        try:
            client_outcome = run_pseudo_client(
                cmd, *cmd_args,
                enabled=enabled,
                state_dir=state_dir,
                rootfs_dir=rootfs_dir,
                tmp_dir=tmp_dir,
                check_for_empty_stderr=check_for_client_empty_stderr,
                check_for_empty_stdout=check_for_client_empty_stdout,
                timeout_s=client_timeout_s
            )
        finally:
            server_process.terminate()
            server_outcome = future_server_outcome.result()

        return PseudoOutcome(
            client=client_outcome,
            server=server_outcome
        )
