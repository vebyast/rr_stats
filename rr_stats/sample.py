import dataclasses
import datetime
import pytz
import sqlite3
import bs4
import requests
from rr_stats import stats
import sys


def _normalize(s: str) -> int:
    return int(s.replace(",", ""))


def _extract_value(stats_content: bs4.Tag, n: int) -> int:
    return _normalize(stats_content.select(f"li:nth-of-type({n})")[0].text)


def _extract_stats(page: bs4.BeautifulSoup) -> stats.Stat:
    soup = bs4.BeautifulSoup(page, "html.parser")
    stats_content = soup.select("div.stats-content > div:nth-of-type(2) > ul")[0]
    return stats.Stat(
        total_views=_extract_value(stats_content, 2),
        average_views=_extract_value(stats_content, 4),
        followers=_extract_value(stats_content, 6),
        favorites=_extract_value(stats_content, 8),
        ratings=_extract_value(stats_content, 10),
        pages=_extract_value(stats_content, 12),
    )


def main():
    page_url = sys.argv[1]
    page = requests.get(page_url).content
    sample = _extract_stats(page)
    db = stats.connect()
    stats.insert_sample(db, sample)
    db.commit()
    db.close()
