"""CLI entry point.

Two modes:
  feed-filter <channel> --min-minutes N --output PATH   # one channel
  feed-filter --config channels.yaml                     # batch, e.g. in CI
"""

import argparse

import yaml

from feed_filter.logger import get_logger
from feed_filter.pipeline import filter_channel

logger = get_logger(__name__)


def run_config(config_path: str) -> None:
    with open(config_path) as f:
        config = yaml.safe_load(f)

    for entry in config.get("channels", []):
        filter_channel(
            channel=entry["url"],
            min_minutes=entry.get("min_minutes", 5.0),
            output=entry["output"],
            self_url=entry.get("self_url"),
        )


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
    args = parser.parse_args()

    if args.config:
        run_config(args.config)
        return

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
