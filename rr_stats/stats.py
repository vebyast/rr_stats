import dataclasses
from typing import Iterator, Callable
import datetime
import pytz
import sqlite3
import bs4
import requests
import xdg
import time
import enum


def _db_path() -> str:
    return xdg.xdg_data_home() / "rr_stats" / "rr_stats.sqlite"


@dataclasses.dataclass
class Stat:
    total_views: int = 0
    average_views: int = 0
    favorites: int = 0
    followers: int = 0
    ratings: int = 0
    pages: int = 0
    timestamp: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(
            pytz.timezone("America/Los_Angeles")
        )
    )


def _db_ensure_inited(cur: sqlite3.Cursor):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS stats ("
        "total_views INT,"
        "average_views INT,"
        "followers INT,"
        "favorites INT,"
        "ratings INT,"
        "pages INT,"
        "timestamp INT"
        ")"
    )


class OpenMode(enum.Enum):
    READ_WRITE = enum.auto()
    READ_ONLY = enum.auto()


def connect(mode: OpenMode = OpenMode.READ_WRITE) -> sqlite3.Connection:
    if mode == OpenMode.READ_ONLY:
        to_uri = lambda p: "file:" + str(p) + "?mode=ro"
    elif mode == OpenMode.READ_WRITE:
        to_uri = lambda p: str(p)

    db = sqlite3.connect(to_uri(_db_path()), uri=True)
    return db


def insert_sample(db: sqlite3.Connection, sample: Stat):
    # list instead of dict so iteration order is stable
    insert_params = [
        ("total_views", sample.total_views),
        ("average_views", sample.average_views),
        ("followers", sample.followers),
        ("favorites", sample.favorites),
        ("ratings", sample.ratings),
        ("pages", sample.pages),
        ("timestamp", sample.timestamp.timestamp()),
    ]
    cur = db.cursor()
    _db_ensure_inited(cur)
    cur.execute(
        "INSERT INTO stats ("
        # column names
        + ", ".join(k for k, v in insert_params) + ") VALUES ("
        # parameter names
        + ", ".join(f":{k}" for k, v in insert_params) + ")",
        # map parameter names to values
        dict(insert_params),
    )


def read_samples(db: sqlite3.Connection) -> Iterator[Stat]:
    cur = db.cursor()
    data = cur.execute(
        "SELECT "
        "  total_views, "
        "  average_views, "
        "  favorites, "
        "  followers, "
        "  ratings, "
        "  pages, "
        "  timestamp "
        "FROM STATS"
    )
    for row in data:
        yield Stat(
            total_views=row[0],
            average_views=row[1],
            favorites=row[2],
            followers=row[3],
            ratings=row[4],
            pages=row[5],
            timestamp=datetime.datetime.fromtimestamp(row[6]),
        )


class _CallbackEventHandler(events.FileSystemEventHandler):
    def __init__(self, cb: Callable[[], None]):
        self.callback = cb

    def on_modified(self, event: events.FileSystemEvent):
        self.callback()


def print_db_path():
    print(_db_path())
