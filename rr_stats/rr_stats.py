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
    follows: int
    ratings: int
    comments: int
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
        favorites=_extract_stat(stats_content, 6),
        follows=_extract_stat(stats_content, 8),
        ratings=_extract_stat(stats_content, 10),
        comments=_extract_stat(stats_content, 12),
    )


def db_init(db):
    cur = db.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS stats ("
        "total_views INT,"
        "average_views INT,"
        "favorites INT,"
        "follows INT,"
        "ratings INT,"
        "comments INT,"
        "timestamp INT"
        ")"
    )


def db_insert_sample(db, sample):
    cur = db.cursor()
    insert_params = {
        "total_views": sample.total_views,
        "average_views": sample.average_views,
        "favorites": sample.favorites,
        "follows": sample.follows,
        "ratings": sample.ratings,
        "comments": sample.comments,
        "timestamp": sample.timestamp.timestamp(),
    }
    cur.execute(
        "INSERT INTO stats VALUES ("
        + ", ".join(f":{k}" for k in insert_params.keys())
        + ")",
        insert_params,
    )


def main():
    db = sqlite3.connect("bia.sqlite")
    db_init(db)
    sample = get_stats(
        "https://www.royalroad.com/fiction/48116/the-bureau-of-isekai-affairs"
    )
    db_insert_sample(db, sample)
    db.commit()
    db.close()
