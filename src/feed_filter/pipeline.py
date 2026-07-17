"""Core pipeline: fetch a channel's feed, filter by duration, build the output feed."""

from datetime import UTC, datetime
from pathlib import Path

from feed_filter.feed_builder import build_combined_feed, build_filtered_feed
from feed_filter.logger import get_logger
from feed_filter.youtube_source import fetch_video_metadata, list_recent_videos

logger = get_logger(__name__)

UNFINISHED_LIVE_STATUSES = {"is_live", "is_upcoming", "post_live"}
DEFAULT_RECENT_COUNT = 20


def filter_channel(
    channel: str,
    min_minutes: float,
    output: str,
    self_url: str | None = None,
    recent_count: int = DEFAULT_RECENT_COUNT,
) -> list:
    """Filter a channel/tab's recent videos by minimum duration and write it to `output`.

    Streams still live, not yet started, or still being processed after ending
    (post_live) are always skipped, regardless of min_minutes, since their
    duration isn't final yet. Only fully finished streams (was_live) and
    regular non-stream videos pass through to the duration check.

    Returns the list of kept entries (each tagged with "_duration_seconds" and
    "_source_title"), so callers can merge them into a combined feed.
    """
    channel_info = list_recent_videos(channel, limit=recent_count)
    channel_title = channel_info["channel_title"]
    channel_link = channel_info["channel_link"]
    video_urls = channel_info["video_urls"]
    logger.info("listed channel videos", channel=channel, video_count=len(video_urls))

    min_seconds = min_minutes * 60
    kept = []
    for video_url in video_urls:
        try:
            metadata = fetch_video_metadata(video_url)
        except Exception as exc:  # noqa: BLE001 - a single bad video shouldn't fail the whole run
            logger.warning("skipping video, metadata lookup failed", url=video_url, error=str(exc))
            continue

        live_status = metadata["live_status"]
        if live_status in UNFINISHED_LIVE_STATUSES:
            logger.info(
                "skipping video, stream not finished yet",
                url=video_url,
                live_status=live_status,
                title=metadata.get("title"),
            )
            continue

        duration = metadata["duration"]
        if duration is None:
            logger.warning("skipping video, unknown duration", url=video_url)
            continue

        keep = duration >= min_seconds
        logger.info(
            "video checked",
            keep=keep,
            duration_seconds=duration,
            title=metadata.get("title"),
        )

        if keep:
            kept.append(
                {
                    "title": metadata.get("title", ""),
                    "link": video_url,
                    "id": f"yt:video:{metadata.get('video_id')}",
                    "published": metadata.get("published"),
                    "updated": metadata.get("published"),
                    "summary": metadata.get("description"),
                    "thumbnail_url": metadata.get("thumbnail"),
                    "_duration_seconds": duration,
                    "_source_title": channel_title,
                }
            )

    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    tree = build_filtered_feed(channel_title, channel_link, kept, generated_at, self_url=self_url)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    logger.info(
        "wrote filtered feed",
        kept=len(kept),
        total=len(video_urls),
        output=str(output_path),
    )
    return kept


def write_combined_feed(
    all_kept: list, output: str, self_url: str | None = None, title: str = "Combined"
) -> None:
    """Merge kept entries from multiple channels into one Atom feed, newest first."""
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    tree = build_combined_feed(all_kept, generated_at, self_url=self_url, title=title)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    logger.info("wrote combined feed", entries=len(all_kept), output=str(output_path))
