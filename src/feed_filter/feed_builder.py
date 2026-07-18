"""Building Atom feeds from a subset of one or more source feeds' entries."""

import html
import xml.etree.ElementTree as ET

ATOM_NS = "http://www.w3.org/2005/Atom"
MEDIA_NS = "http://search.yahoo.com/mrss/"

# Public WebSub (formerly PubSubHubbub) hub. Declaring it here plus pinging it
# after every publish (see websub.ping_hub) lets hub-aware readers like Feedly
# get near-instant updates instead of waiting on their own polling schedule.
WEBSUB_HUB_URL = "https://pubsubhubbub.appspot.com/"

ET.register_namespace("", ATOM_NS)
ET.register_namespace("media", MEDIA_NS)


def _build_entry_element(
    entry: dict, generated_at: str, include_author: bool = False
) -> ET.Element:
    """Build a single <entry>. entry must carry a "_duration_seconds" key.

    If include_author is set, entry's "_source_title" (the channel it came from)
    is added as an <author>, so a reader merging multiple channels can tell them
    apart.
    """
    entry_el = ET.Element(f"{{{ATOM_NS}}}entry")

    e_title = ET.SubElement(entry_el, f"{{{ATOM_NS}}}title")
    e_title.text = entry.get("title", "")

    e_link = ET.SubElement(entry_el, f"{{{ATOM_NS}}}link")
    e_link.set("rel", "alternate")
    e_link.set("href", entry.get("link", ""))

    e_id = ET.SubElement(entry_el, f"{{{ATOM_NS}}}id")
    e_id.text = entry.get("id", entry.get("link", ""))

    if include_author and entry.get("_source_title"):
        author_el = ET.SubElement(entry_el, f"{{{ATOM_NS}}}author")
        name_el = ET.SubElement(author_el, f"{{{ATOM_NS}}}name")
        name_el.text = entry["_source_title"]

    published = entry.get("published")
    if published:
        e_pub = ET.SubElement(entry_el, f"{{{ATOM_NS}}}published")
        e_pub.text = published

    e_updated = ET.SubElement(entry_el, f"{{{ATOM_NS}}}updated")
    e_updated.text = entry.get("updated", published or generated_at)

    summary = entry.get("summary")
    if summary:
        e_summary = ET.SubElement(entry_el, f"{{{ATOM_NS}}}summary")
        e_summary.text = summary

    thumbnail_url = entry.get("thumbnail_url")
    if thumbnail_url:
        e_thumbnail = ET.SubElement(entry_el, f"{{{MEDIA_NS}}}thumbnail")
        e_thumbnail.set("url", thumbnail_url)

        # Readers that don't parse the media: namespace (e.g. NetNewsWire)
        # still show a per-item thumbnail if it's embedded as an <img> in the
        # entry's HTML content, which is far more universally supported.
        body_html = f'<img src="{html.escape(thumbnail_url)}"><br>'
        if summary:
            body_html += html.escape(summary).replace("\n", "<br>")
        e_content = ET.SubElement(entry_el, f"{{{ATOM_NS}}}content")
        e_content.set("type", "html")
        e_content.text = body_html

    duration_el = ET.SubElement(entry_el, f"{{{MEDIA_NS}}}duration_seconds")
    duration_el.text = str(entry["_duration_seconds"])

    return entry_el


def build_filtered_feed(
    channel_title: str,
    channel_link: str,
    entries: list,
    generated_at: str,
    self_url: str | None = None,
) -> ET.ElementTree:
    """Build an Atom feed tree containing only the given entries from one channel."""
    feed_el = ET.Element(f"{{{ATOM_NS}}}feed")

    title = ET.SubElement(feed_el, f"{{{ATOM_NS}}}title")
    title.text = f"{channel_title} (filtered)"

    link = ET.SubElement(feed_el, f"{{{ATOM_NS}}}link")
    link.set("rel", "alternate")
    link.set("href", channel_link)

    if self_url:
        self_link = ET.SubElement(feed_el, f"{{{ATOM_NS}}}link")
        self_link.set("rel", "self")
        self_link.set("href", self_url)

        hub_link = ET.SubElement(feed_el, f"{{{ATOM_NS}}}link")
        hub_link.set("rel", "hub")
        hub_link.set("href", WEBSUB_HUB_URL)

    feed_id = ET.SubElement(feed_el, f"{{{ATOM_NS}}}id")
    feed_id.text = channel_link

    feed_updated = ET.SubElement(feed_el, f"{{{ATOM_NS}}}updated")
    feed_updated.text = generated_at

    for entry in entries:
        feed_el.append(_build_entry_element(entry, generated_at))

    return ET.ElementTree(feed_el)


def build_combined_feed(
    entries: list,
    generated_at: str,
    self_url: str | None = None,
    title: str = "Combined",
) -> ET.ElementTree:
    """Build an Atom feed merging entries from multiple channels, newest first.

    Each entry must carry "_duration_seconds" and "_source_title" (set by the
    caller to identify which channel it came from).
    """
    feed_el = ET.Element(f"{{{ATOM_NS}}}feed")

    title_el = ET.SubElement(feed_el, f"{{{ATOM_NS}}}title")
    title_el.text = title

    if self_url:
        self_link = ET.SubElement(feed_el, f"{{{ATOM_NS}}}link")
        self_link.set("rel", "self")
        self_link.set("href", self_url)

        hub_link = ET.SubElement(feed_el, f"{{{ATOM_NS}}}link")
        hub_link.set("rel", "hub")
        hub_link.set("href", WEBSUB_HUB_URL)

    feed_id = ET.SubElement(feed_el, f"{{{ATOM_NS}}}id")
    feed_id.text = self_url or f"urn:feed-filter:combined:{title.lower().replace(' ', '-')}"

    feed_updated = ET.SubElement(feed_el, f"{{{ATOM_NS}}}updated")
    feed_updated.text = generated_at

    sorted_entries = sorted(
        entries, key=lambda e: e.get("published", e.get("updated", "")), reverse=True
    )
    for entry in sorted_entries:
        feed_el.append(_build_entry_element(entry, generated_at, include_author=True))

    return ET.ElementTree(feed_el)
