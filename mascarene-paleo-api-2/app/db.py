from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "mascarene_paleo.sqlite"


def database_path() -> Path:
    return Path(os.getenv("MASCARENE_PALEO_DB", str(DEFAULT_DB)))


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    con = sqlite3.connect(database_path())
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]
