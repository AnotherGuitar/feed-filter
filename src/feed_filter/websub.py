"""Notifying a WebSub (PubSubHubbub) hub after publishing, so hub-aware
readers like Feedly get near-instant updates instead of waiting on their own
polling schedule.

Must be called after the new content is actually live at feed_url (i.e.
after git push), since the hub re-fetches feed_url itself upon being pinged.
"""

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from feed_filter.feed_builder import WEBSUB_HUB_URL
from feed_filter.logger import get_logger

logger = get_logger(__name__)


def ping_hub(feed_url: str, hub_url: str = WEBSUB_HUB_URL) -> None:
    """Tell the hub that feed_url has new content."""
    data = urlencode({"hub.mode": "publish", "hub.url": feed_url}).encode()
    req = Request(hub_url, data=data)
    try:
        with urlopen(req, timeout=10) as resp:
            logger.info("pinged websub hub", feed_url=feed_url, status=resp.status)
    except Exception as exc:  # noqa: BLE001 - a failed ping shouldn't break the publish run
        logger.warning("websub hub ping failed", feed_url=feed_url, error=str(exc))
