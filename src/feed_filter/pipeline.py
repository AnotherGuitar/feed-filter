"""Core pipeline: fetch a channel's feed, filter by duration, build the output feed."""

from datetime import UTC, datetime
from pathlib import Path

from feed_filter.feed_builder import build_combined_feed, build_filtered_feed
from feed_filter.logger import get_logger
from feed_filter.youtube_source import fetch_feed, fetch_video_metadata, resolve_channel_id

logger = get_logger(__name__)

UNFINISHED_LIVE_STATUSES = {"is_live", "is_upcoming"}


def filter_channel(
    channel: str, min_minutes: float, output: str, self_url: str | None = None
) -> list:
    """Filter one channel's feed by minimum video duration and write it to `output`.

    Streams still in progress or not yet started are always skipped, regardless
    of min_minutes, since their duration isn't final yet.

    Returns the list of kept entries (each tagged with "_duration_seconds" and
    "_source_title"), so callers can merge them into a combined feed.
    """
    channel_id = resolve_channel_id(channel)
    logger.info("resolved channel", channel=channel, channel_id=channel_id)

    source_feed = fetch_feed(channel_id)
    logger.info("fetched feed", entry_count=len(source_feed.entries))

    source_title = source_feed.feed.get("title", "")
    min_seconds = min_minutes * 60
    kept = []
    for entry in source_feed.entries:
        video_url = entry.get("link")
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
                title=entry.get("title"),
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
            title=entry.get("title"),
        )

        if keep:
            entry["_duration_seconds"] = duration
            entry["_source_title"] = source_title
            kept.append(entry)

    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    tree = build_filtered_feed(source_feed, kept, generated_at, self_url=self_url)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    logger.info(
        "wrote filtered feed",
        kept=len(kept),
        total=len(source_feed.entries),
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
