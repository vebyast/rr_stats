import dataclasses
import datetime
import pytz
import sqlite3
import bs4
import requests


def _normalize(s: str) -> int:
    return int(s.replace(",", ""))


def _extract_stat(stats_content, n):
    return _normalize(stats_content.select(f"li:nth-of-type({n})")[0].text)


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


def get_stats(url: str) -> Stat:
    page = requests.get(url).content
    soup = bs4.BeautifulSoup(page, "html.parser")
    stats_content = soup.select("div.stats-content > div:nth-of-type(2) > ul")[0]
    return Stat(
        total_views=_extract_stat(stats_content, 2),
        average_views=_extract_stat(stats_content, 4),
        followers=_extract_stat(stats_content, 6),
        favorites=_extract_stat(stats_content, 8),
        ratings=_extract_stat(stats_content, 10),
        pages=_extract_stat(stats_content, 12),
    )


def _db_init(db):
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


def _db_insert_sample(db, sample):
    cur = db.cursor()
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


def read_db(path):
    db = sqlite3.connect(path)
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


def main():
    db = sqlite3.connect("bia.sqlite")
    _db_init(db)
    sample = get_stats(
        "https://www.royalroad.com/fiction/48116/the-bureau-of-isekai-affairs"
    )
    _db_insert_sample(db, sample)
    db.commit()
    db.close()
