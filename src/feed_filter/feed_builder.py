"""Building a filtered Atom feed from a subset of a source feed's entries."""

import xml.etree.ElementTree as ET

ATOM_NS = "http://www.w3.org/2005/Atom"
MEDIA_NS = "http://search.yahoo.com/mrss/"

ET.register_namespace("", ATOM_NS)
ET.register_namespace("media", MEDIA_NS)


def build_filtered_feed(
    source_feed,
    entries: list,
    generated_at: str,
    self_url: str | None = None,
) -> ET.ElementTree:
    """Build an Atom feed tree containing only the given entries.

    entries must each carry a "_duration_seconds" key, added by the caller after
    filtering by duration.
    """
    feed_el = ET.Element(f"{{{ATOM_NS}}}feed")

    title = ET.SubElement(feed_el, f"{{{ATOM_NS}}}title")
    title.text = f"{source_feed.feed.get('title', 'Filtered feed')} (filtered)"

    link = ET.SubElement(feed_el, f"{{{ATOM_NS}}}link")
    link.set("rel", "alternate")
    link.set("href", source_feed.feed.get("link", ""))

    if self_url:
        self_link = ET.SubElement(feed_el, f"{{{ATOM_NS}}}link")
        self_link.set("rel", "self")
        self_link.set("href", self_url)

    feed_id = ET.SubElement(feed_el, f"{{{ATOM_NS}}}id")
    feed_id.text = source_feed.feed.get("id", source_feed.feed.get("link", ""))

    feed_updated = ET.SubElement(feed_el, f"{{{ATOM_NS}}}updated")
    feed_updated.text = generated_at

    for entry in entries:
        entry_el = ET.SubElement(feed_el, f"{{{ATOM_NS}}}entry")

        e_title = ET.SubElement(entry_el, f"{{{ATOM_NS}}}title")
        e_title.text = entry.get("title", "")

        e_link = ET.SubElement(entry_el, f"{{{ATOM_NS}}}link")
        e_link.set("rel", "alternate")
        e_link.set("href", entry.get("link", ""))

        e_id = ET.SubElement(entry_el, f"{{{ATOM_NS}}}id")
        e_id.text = entry.get("id", entry.get("link", ""))

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

        duration_el = ET.SubElement(entry_el, f"{{{MEDIA_NS}}}duration_seconds")
        duration_el.text = str(entry["_duration_seconds"])

    return ET.ElementTree(feed_el)
