import logging

import pytest
from _pytest.tmpdir import TempPathFactory
from test_lib import (run_pseudo, get_data_root_dir,
                      iter_pseudo_files_db_rows)

LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize("script_rel_filename", [
    "rename/existing_target.sh",
    "rename/existing_target_inode_reused.sh"
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

    cmd_path = get_data_root_dir().joinpath("cmd_cases", script_rel_filename)
    compl_proc = run_pseudo(
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

    LOGGER.info(f"state_dir: {state_dir}")
    file_db_path = state_dir.joinpath("files.db")
    assert state_dir.joinpath("files.db").exists()

    LOGGER.info(f"file_db_path: {file_db_path}")
    rows = list(iter_pseudo_files_db_rows(
        file_db_path,
        timeout_s=45.0
    ))
    assert len(rows) == 2
    LOGGER.info("file_db_rows: {rows}")
