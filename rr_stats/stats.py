import dataclasses
from typing import Iterator
import datetime
import pytz
import sqlite3
import bs4
import requests
import xdg


@dataclasses.dataclass
class Stat:
    total_views: int
    average_views: int
    favorites: int
    followers: int
    ratings: int
    pages: int
    timestamp: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(
            pytz.timezone("America/Los_Angeles")
        )
    )


def _db_ensure_inited(db: sqlite3.Connection):
    cur = db.cursor()
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


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(xdg.xdg_data_home() / "rr_stats" / "rr_stats.sqlite")
    _db_ensure_inited(db)
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
    cur.execute(
        "INSERT INTO stats ("
        # column names
        + ", ".join(k for k, v in insert_params)
        +") VALUES ("
        # parameter names
        + ", ".join(f":{k}" for k, v in insert_params)
        + ")",
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

