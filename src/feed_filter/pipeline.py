"""Core pipeline: fetch a channel's feed, filter by duration, build the output feed."""

from datetime import UTC, datetime
from pathlib import Path

from feed_filter.feed_builder import build_filtered_feed
from feed_filter.logger import get_logger
from feed_filter.youtube_source import fetch_feed, resolve_channel_id, video_duration_seconds

logger = get_logger(__name__)


def filter_channel(
    channel: str, min_minutes: float, output: str, self_url: str | None = None
) -> int:
    """Filter one channel's feed by minimum video duration and write it to `output`.

    Returns the number of entries kept.
    """
    channel_id = resolve_channel_id(channel)
    logger.info("resolved channel", channel=channel, channel_id=channel_id)

    source_feed = fetch_feed(channel_id)
    logger.info("fetched feed", entry_count=len(source_feed.entries))

    min_seconds = min_minutes * 60
    kept = []
    for entry in source_feed.entries:
        video_url = entry.get("link")
        try:
            duration = video_duration_seconds(video_url)
        except Exception as exc:  # noqa: BLE001 - a single bad video shouldn't fail the whole run
            logger.warning("skipping video, duration lookup failed", url=video_url, error=str(exc))
            continue

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
    return len(kept)
