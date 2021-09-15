import logging

import pytest
from typing import Iterator
from pathlib import Path
from _pytest.tmpdir import TempPathFactory
from test_lib import (run_pseudo, get_data_root_dir,
                      iter_pseudo_files_db_rows)

LOGGER = logging.getLogger(__name__)


def _iter_files_under(root_dir: Path) -> Iterator[Path]:
    if not root_dir.exists():
        return

    for file in root_dir.iterdir():
        if file.is_dir():
            yield from _iter_files_under(file)
        else:
            yield file


@pytest.mark.parametrize("script_rel_filename", [
    "250_opencreate/300_two_files.sh",
    "400_create/400_inode_reuse_after_delete.sh",
    "750_rename/100_no_target.sh",
    "750_rename/200_existing_target.sh",
    "750_rename/250_existing_target_twice.sh",
    "750_rename/255_existing_target_twice_alt.sh",
    "750_rename/275_existing_target_contorted.sh",
    "750_rename/500_existing_target_inode_reused.sh",
    "750_rename/505_existing_target_inode_reused_alt.sh"
])
def test_pseudo_cmd_case(
        tmp_path_factory: TempPathFactory,
        script_rel_filename: str
) -> None:
    tmp_dir = tmp_path_factory.mktemp("cmd_case")
    state_dir = tmp_dir.joinpath("pseudo_state")
    state_dir.mkdir(parents=True)
    rootfs_dir = tmp_dir.joinpath("pseudo_rootfs")
    rootfs_dir.mkdir(parents=True)

    LOGGER.info(f"state_dir: '{state_dir}'.")
    LOGGER.info(f"rootfs_dir: '{rootfs_dir}'.")

    cmd_path = get_data_root_dir().joinpath("cmd_cases", script_rel_filename)
    run_pseudo(
        cmd_path,
        enabled=True,
        tmp_dir=tmp_dir,
        state_dir=state_dir,
        rootfs_dir=rootfs_dir,
        check_for_client_empty_stderr=True,
        check_for_client_empty_stdout=True,
        check_for_server_empty_stderr=False,
        check_for_server_empty_stdout=False
    )

    rootfs_files = list(_iter_files_under(rootfs_dir))
    rootfs_files_log_str = "\n".join(
        f"{{file: {f}, inode: {f.stat().st_ino}}}"
        for f in rootfs_files
    )
    LOGGER.info(
        f"RootFs contains the following files:\n{rootfs_files_log_str}")

    file_db_path = state_dir.joinpath("files.db")
    LOGGER.info(f"file_db_path: '{file_db_path}'.")
    assert file_db_path.exists()

    rows = list(iter_pseudo_files_db_rows(
        file_db_path,
        timeout_s=45.0
    ))

    LOGGER.info(f"len(rows): {len(rows)}")

    rows_by_path = {
        r.path: r for r in rows
    }

    rows_by_inode = {
        r.ino: r for r in rows
    }

    rows_log_str = "\n".join(
        f"{{path: {r.path}, ino: {r.ino}, deleting: {r.deleting}}}"
        for r in rows
    )
    LOGGER.info(f"'{file_db_path}' contains:\n{rows_log_str}")

    try:
        for f in rootfs_files:
            LOGGER.info(f"Performing checks for rootfs file '{f}'.")
            inode = f.stat().st_ino
            try:
                f_row = rows_by_path[f]
            except KeyError as e:
                raise AssertionError(
                    f"Missing row for the '{f}' file path."
                ) from e

            assert inode == f_row.ino, (
                f"Row for file path {f} has erreneous inode '{f_row.ino}'. "
                f"Expected inode '{inode}'."
            )

            try:
                inode_row = rows_by_inode[inode]
            except KeyError as e:
                raise AssertionError(
                    f"Missing row for inode '{inode}' obtained via stats "
                    f"over the real '{f}' file path."
                ) from e

            assert f == inode_row.path, (
                f"Row for inode '{inode}' has erroneous file path "
                f"'{inode_row.path}'. Expected file path '{f}'."
            )

    except AssertionError as e:
        raise AssertionError(
            f"Erroneous '{str(file_db_path)}': {e}") from e


    try:
        for row in rows:
            assert row.path.exists(), (
                f"Missing file '{row.path}' for row with id '{row.id}'."
            )
    except AssertionError as e:
        raise AssertionError(
            f"Erroneous '{str(file_db_path)}': {e}") from e
