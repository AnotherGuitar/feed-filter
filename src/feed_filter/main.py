"""CLI entry point.

Two modes:
  feed-filter <channel> --min-minutes N --output PATH   # one channel
  feed-filter --config channels.yaml                     # batch, e.g. in CI

Exit codes for --config mode: 0 if every channel succeeded, 2 if one or more
channels were still failing after all retry passes (whatever did succeed is
still written/combined - this just flags that something's missing).
"""

import argparse
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import yaml

from feed_filter.logger import get_logger
from feed_filter.pipeline import filter_channel, write_combined_feed

logger = get_logger(__name__)

MAX_EXTRA_PASSES = 3
PASS_RETRY_DELAY = 30.0
DEFAULT_SUMMARY_PATH = "logs/last_run_summary.txt"


def _write_error_summary(summary_path: str, errors: dict) -> None:
    """Write a plain-text (no ANSI/structlog noise) summary of what got skipped."""
    path = Path(summary_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"feed-filter run at {datetime.now(UTC).isoformat()}",
        "",
        "The following channels were skipped after all retry passes:",
        "",
    ]
    for name, error in errors.items():
        lines.append(f"- {name}: {error}")
    path.write_text("\n".join(lines) + "\n")


def run_config(config_path: str, summary_path: str = DEFAULT_SUMMARY_PATH) -> int:
    """Process every channel, retrying failed ones in later passes.

    Returns 0 if every channel eventually succeeded, 2 if any channel was
    still failing after all passes (a readable summary is also written to
    summary_path in that case).
    """
    with open(config_path) as f:
        config = yaml.safe_load(f)

    pending = config.get("channels", [])
    all_kept = []
    last_errors: dict = {}

    delay = PASS_RETRY_DELAY
    for pass_num in range(1, MAX_EXTRA_PASSES + 2):
        still_pending = []
        for entry in pending:
            name = entry.get("name", entry.get("url"))
            try:
                kept = filter_channel(
                    channel=entry["url"],
                    min_minutes=entry.get("min_minutes", 5.0),
                    output=entry["output"],
                    self_url=entry.get("self_url"),
                )
            except Exception as exc:  # noqa: BLE001 - one channel's failure shouldn't skip the rest
                logger.warning(
                    "channel failed this pass, will retry later",
                    name=name,
                    pass_num=pass_num,
                    error=str(exc),
                )
                last_errors[name] = str(exc)
                still_pending.append(entry)
                continue
            last_errors.pop(name, None)
            all_kept.extend(kept)

        pending = still_pending
        if not pending:
            break
        if pass_num <= MAX_EXTRA_PASSES:
            logger.warning(
                "retrying failed channels after backoff",
                channels=[e.get("name", e.get("url")) for e in pending],
                delay_seconds=delay,
            )
            time.sleep(delay)
            delay *= 2

    combined_output = config.get("combined_output")
    if combined_output:
        write_combined_feed(
            all_kept,
            combined_output,
            self_url=config.get("combined_self_url"),
            title=config.get("combined_title", "Combined"),
        )

    if last_errors:
        logger.error(
            "channels still failing after all retry passes - some content was skipped",
            channels=last_errors,
        )
        _write_error_summary(summary_path, last_errors)
        return 2

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "channel",
        nargs="?",
        help="Channel URL, @handle, or channel_id, e.g. https://www.youtube.com/@thegrayzone7996/videos",
    )
    parser.add_argument(
        "--min-minutes",
        type=float,
        default=5.0,
        help="Minimum video duration in minutes to keep (default: 5)",
    )
    parser.add_argument(
        "--output",
        default="filtered_feed.xml",
        help="Path to write the filtered Atom feed (default: filtered_feed.xml)",
    )
    parser.add_argument(
        "--self-url",
        default=None,
        help=(
            "Public URL this feed will be hosted at, written as the feed's "
            "<link rel=self> (optional)"
        ),
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a channels.yaml to batch-process instead of a single channel",
    )
    parser.add_argument(
        "--summary-path",
        default=DEFAULT_SUMMARY_PATH,
        help=(
            "Where to write the plain-text skipped-channels summary, only used "
            f"with --config (default: {DEFAULT_SUMMARY_PATH})"
        ),
    )
    args = parser.parse_args()

    if args.config:
        sys.exit(run_config(args.config, summary_path=args.summary_path))

    if not args.channel:
        parser.error("channel is required unless --config is given")

    filter_channel(
        channel=args.channel,
        min_minutes=args.min_minutes,
        output=args.output,
        self_url=args.self_url,
    )


if __name__ == "__main__":
    main()
