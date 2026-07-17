"""Listing a YouTube channel's videos (scoped to whatever tab its URL points at)
and fetching per-video metadata, all via yt-dlp.

This intentionally doesn't use YouTube's RSS feed: RSS is channel-wide (it
ignores /streams, /shorts, etc. and just returns the latest 15 uploads across
the whole channel), so it can't honor "only this tab" and can miss content
entirely if the channel posts frequently on other tabs.
"""

import time
from datetime import UTC, datetime

import yt_dlp

from feed_filter.logger import get_logger

logger = get_logger(__name__)

YDL_BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    # The default "web" client reliably triggers YouTube's bot check in
    # headless environments; "android" doesn't need cookies/sign-in.
    "extractor_args": {"youtube": {"player_client": ["android"]}},
}


def normalize_channel_url(channel_ref: str) -> str:
    """Accept a bare @handle or a full URL and return a URL yt-dlp can extract."""
    if channel_ref.startswith("http"):
        return channel_ref
    handle = channel_ref.lstrip("@")
    return f"https://www.youtube.com/@{handle}"


def list_recent_videos(channel_url: str, limit: int = 20, retries: int = 5) -> dict:
    """List a channel/tab's most recent videos, newest first.

    Respects whatever tab the URL points to (videos, streams, shorts, ...).
    Returns {"channel_title", "channel_link", "video_urls": [str, ...]}.
    """
    url = normalize_channel_url(channel_url)
    opts = {**YDL_BASE_OPTS, "extract_flat": "in_playlist", "playlistend": limit}

    delay = 2.0
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            entries = list(info.get("entries", []) or [])
            return {
                "channel_title": info.get("channel") or info.get("uploader") or url,
                "channel_link": info.get("channel_url") or info.get("uploader_url") or url,
                "video_urls": [e["url"] for e in entries if e.get("url")],
            }
        except Exception as exc:  # noqa: BLE001 - broad on purpose, we retry on any failure
            last_error = exc
            logger.warning(
                "channel listing attempt failed, retrying", attempt=attempt, error=str(exc)
            )
            time.sleep(delay)
            delay *= 2

    raise RuntimeError(f"Failed to list videos for {url} after {retries} attempts: {last_error}")


def fetch_video_metadata(video_url: str) -> dict:
    """Fetch a video's full metadata: title, description, thumbnail, duration,
    live_status, and published date.

    live_status is one of: is_live, is_upcoming, post_live, was_live, or None
    for a regular (never-live) video. A stream still in progress, not yet
    started, or still being processed reports duration as None/0, so callers
    should check live_status before trusting duration.
    """
    with yt_dlp.YoutubeDL(YDL_BASE_OPTS) as ydl:
        info = ydl.extract_info(video_url, download=False)

    duration = info.get("duration")
    published = _extract_published(info)

    return {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "description": info.get("description"),
        "thumbnail": info.get("thumbnail"),
        "duration": int(duration) if duration is not None else None,
        "live_status": info.get("live_status"),
        "published": published,
    }


def _extract_published(info: dict) -> str | None:
    timestamp = info.get("timestamp")
    if timestamp is not None:
        return datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z")

    upload_date = info.get("upload_date")
    if upload_date:
        return (
            datetime.strptime(upload_date, "%Y%m%d")
            .replace(tzinfo=UTC)
            .isoformat()
            .replace("+00:00", "Z")
        )

    return None
