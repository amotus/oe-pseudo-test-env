
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from typing import Iterator, Tuple, Any, Optional
from pathlib import Path


@dataclass
class PseudoFilesDbRow:
    id: int
    path: Path
    dev: int
    ino: int
    uid: int
    gid: int
    mode: int
    rdev: int
    deleting: int


class PseudoFilesDbError(Exception):
    pass


class PseudoFilesDbRowParseError(PseudoFilesDbError):
    pass


def _parse_db_int(db_v: Any) -> int:
    if not isinstance(db_v, int):
        raise PseudoFilesDbRowParseError(
            f"Unexpected db value '{db_v}' of type "
            f"'{db_v.__class__.__name__}'. Expected an 'int'."
        )

    return db_v


def _parse_db_str(db_v: Any) -> str:
    if not isinstance(db_v, str):
        raise PseudoFilesDbRowParseError(
            f"Unexpected db value '{db_v}' of type "
            f"'{db_v.__class__.__name__}'. Expected a 'str'."
        )

    return db_v


def _parse_db_path(db_v: Any) -> Path:
    return Path(_parse_db_str(db_v))


def _parse_files_db_row(row: Tuple[Any, ...]) -> PseudoFilesDbRow:
    try:
        return PseudoFilesDbRow(
            id=_parse_db_int(row[0]),
            path=_parse_db_path(row[1]),
            dev=_parse_db_int(row[2]),
            ino=_parse_db_int(row[3]),
            uid=_parse_db_int(row[4]),
            gid=_parse_db_int(row[5]),
            mode=_parse_db_int(row[6]),
            rdev=_parse_db_int(row[7]),
            deleting=_parse_db_int(row[8])
        )
    except IndexError as e:
        raise PseudoFilesDbRowParseError(
            f"Unexpected db row size. Original error: {str(e)}"
        )


def iter_pseudo_files_db_rows(
        db_path: Path,
        timeout_s: Optional[float] = None
) -> Iterator[PseudoFilesDbRow]:
    if timeout_s is None:
        timeout_s = 5.0

    with closing(sqlite3.connect(
        str(db_path),
        timeout=timeout_s
    )) as con:
        with closing(con.cursor()) as cur:
            for row in cur.execute(
                    "SELECT * FROM files ORDER BY id"):
                yield _parse_files_db_row(row)

