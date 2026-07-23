"""Fetching a blog's RSS/Atom feed and normalizing entries to feed_filter's
common shape, so non-YouTube sources can merge into the same output feeds.
"""

from datetime import UTC, datetime

import feedparser

from feed_filter.logger import get_logger

logger = get_logger(__name__)


def _to_iso(parsed_time: tuple | None) -> str | None:
    if not parsed_time:
        return None
    year, month, day, hour, minute, second = parsed_time[:6]
    return (
        datetime(year, month, day, hour, minute, second, tzinfo=UTC)
        .isoformat()
        .replace("+00:00", "Z")
    )


def list_recent_entries(feed_url: str, limit: int) -> dict:
    """Fetch feed_url and return its most recent `limit` entries.

    Trusts the feed's own ordering (newest first) rather than re-sorting -
    true for essentially every blog RSS/Atom feed in practice.

    Returns {"feed_title", "feed_link", "entries": [{"title", "link", "id",
    "published", "summary"}, ...]}.
    """
    parsed = feedparser.parse(feed_url)
    if parsed.get("bozo") and not parsed.entries:
        raise RuntimeError(f"failed to parse feed {feed_url}: {parsed.get('bozo_exception')}")

    feed_title = parsed.feed.get("title") or feed_url
    feed_link = parsed.feed.get("link") or feed_url

    entries = []
    for raw in parsed.entries[:limit]:
        link = raw.get("link", "")
        entries.append(
            {
                "title": raw.get("title", ""),
                "link": link,
                "id": raw.get("id") or link,
                "published": _to_iso(raw.get("published_parsed") or raw.get("updated_parsed")),
                "summary": raw.get("summary", ""),
            }
        )

    logger.info("listed blog entries", feed=feed_url, entry_count=len(entries))
    return {"feed_title": feed_title, "feed_link": feed_link, "entries": entries}
