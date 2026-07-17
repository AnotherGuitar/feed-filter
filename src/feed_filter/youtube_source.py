"""Fetching YouTube channel RSS feeds and per-video durations."""

import re
import time
from urllib.request import Request, urlopen

import feedparser
import yt_dlp

from feed_filter.logger import get_logger

logger = get_logger(__name__)

CHANNEL_ID_RE = re.compile(r"UC[\w-]{22}")


def resolve_channel_id(channel_ref: str) -> str:
    """Accept a channel_id, @handle, or full channel/handle URL and return the channel_id."""
    if re.fullmatch(CHANNEL_ID_RE, channel_ref):
        return channel_ref

    url = channel_ref
    if not url.startswith("http"):
        handle = url.lstrip("@")
        url = f"https://www.youtube.com/@{handle}"

    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    match = re.search(r'"channelId":"(UC[\w-]{22})"', html) or re.search(
        r'"externalId":"(UC[\w-]{22})"', html
    )
    if not match:
        raise ValueError(f"Could not resolve channel id from {channel_ref}")
    return match.group(1)


def fetch_feed(
    channel_id: str, retries: int = 5, initial_delay: float = 2.0
) -> feedparser.FeedParserDict:
    """YouTube's RSS endpoint is flaky and intermittently 404s/500s; retry with backoff."""
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})

    last_status = None
    delay = initial_delay
    for attempt in range(1, retries + 1):
        try:
            with urlopen(req) as resp:
                if resp.status == 200:
                    return feedparser.parse(resp.read())
                last_status = resp.status
        except Exception as exc:  # noqa: BLE001 - broad on purpose, we retry on any failure
            last_status = exc
        logger.warning(
            "feed fetch attempt failed, retrying", attempt=attempt, error=str(last_status)
        )
        time.sleep(delay)
        delay *= 2

    raise RuntimeError(
        f"Failed to fetch feed for channel {channel_id} after {retries} attempts: {last_status}"
    )


def fetch_video_metadata(video_url: str) -> dict:
    """Look up a video's duration and live status via yt-dlp.

    Forces the "android" player client: the default "web" client reliably triggers
    YouTube's bot check in headless environments, while "android" doesn't need
    cookies/sign-in.

    live_status is one of: is_live, is_upcoming, was_live, post_live, not_live, or
    None for a regular (never-live) video. A stream still in progress or not yet
    started reports duration as None/0, so callers should check live_status before
    trusting duration.
    """
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        duration = info.get("duration")
        return {
            "duration": int(duration) if duration is not None else None,
            "live_status": info.get("live_status"),
        }
