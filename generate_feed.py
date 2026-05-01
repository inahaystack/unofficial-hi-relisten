#!/usr/bin/env python3
"""
generate_feed.py

Reads schedule.csv and episodes.json, emits feed.xml containing only
episodes whose publish_date <= now (UTC).

Run locally:  python3 generate_feed.py
Run in CI:    same command; GitHub Actions provides current time.
"""

import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from dateutil.parser import parse as parse_date  # pip install python-dateutil

# ── Configuration ────────────────────────────────────────────────────────────

FEED_TITLE       = "Unofficial Hello Internet Relisten"
FEED_LINK        = "https://raw.githubusercontent.com/inahaystack/unofficial-hi-relisten/refs/heads/main/feed.xml"
FEED_DESCRIPTION = "The original Hello Internet files, republished on Fridays starting May 1st, 2026. For discussion, see the newly liberated subreddit http://old.reddit.com/r/HelloInternet. Long live the Tims!"
FEED_IMAGE       = "https://raw.githubusercontent.com/inahaystack/unofficial-hi-relisten/refs/heads/main/The_Union_Tim_Square.png"
FEED_AUTHOR      = "Tim"
FEED_LANGUAGE    = "en"

SCHEDULE_FILE  = "schedule.csv"
EPISODES_FILE  = "episodes.json"
OUTPUT_FILE    = "feed.xml"

# ── Namespaces ────────────────────────────────────────────────────────────────

NS = {
    "itunes":  "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "atom":    "http://www.w3.org/2005/Atom",
}

for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

def itunes(tag):
    return f"{{{NS['itunes']}}}{tag}"

def content(tag):
    return f"{{{NS['content']}}}{tag}"

def atom(tag):
    return f"{{{NS['atom']}}}{tag}"

# ── Load data ─────────────────────────────────────────────────────────────────

def load_schedule():
    with open(SCHEDULE_FILE, newline="", encoding="utf-8") as f:
        return {row["guid"]: row for row in csv.DictReader(f)}
import os
_override = os.environ.get("FEED_DATE")
now = datetime.fromisoformat(_override).replace(tzinfo=timezone.utc) if _override else datetime.now(timezone.utc)
def load_episodes():
    with open(EPISODES_FILE, encoding="utf-8") as f:
        return {ep["guid"]: ep for ep in json.load(f)}

# ── Build feed ────────────────────────────────────────────────────────────────

def build_feed(schedule, episodes):
    now = datetime.now(timezone.utc)

    due = []
    for guid, row in schedule.items():
        pub_str = row.get("publish_date", "").strip()
        if not pub_str:
            continue
        try:
            pub_dt = parse_date(pub_str)
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if pub_dt <= now and guid in episodes:
            due.append((pub_dt, guid))

    # Most recent first (standard podcast feed order)
    due.sort(reverse=True)

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    def sub(parent, tag, text=None, **attrib):
        e = ET.SubElement(parent, tag, attrib)
        if text is not None:
            e.text = text
        return e

    sub(channel, "title",       FEED_TITLE)
    sub(channel, "link",        FEED_LINK)
    sub(channel, "description", FEED_DESCRIPTION)
    sub(channel, "language",    FEED_LANGUAGE)
    sub(channel, "lastBuildDate", format_datetime(now))
    sub(channel, atom("link"), href=FEED_LINK + "/feed.xml",
        rel="self", type="application/rss+xml")

    sub(channel, itunes("author"),   FEED_AUTHOR)
    sub(channel, itunes("explicit"), "no")
    sub(channel, itunes("image"),    href=FEED_IMAGE)   # channel-level artwork

    img = ET.SubElement(channel, "image")
    sub(img, "url",   FEED_IMAGE)
    sub(img, "title", FEED_TITLE)
    sub(img, "link",  FEED_LINK)

    for pub_dt, guid in due:
        ep = episodes[guid]
        item = ET.SubElement(channel, "item")

        sub(item, "title",   ep["title"])
        sub(item, "pubDate", format_datetime(pub_dt))
        sub(item, "guid",    guid, isPermaLink="false")

        if ep.get("link"):
            sub(item, "link", ep["link"])

        if ep.get("description_html"):
            sub(item, "description", ep["description_html"])
            sub(item, content("encoded"), ep["description_html"])

        if ep.get("op3_audio_url"):
            # Use op3-prefixed URL; fall back to raw if missing
            audio_url = ep["op3_audio_url"]
        else:
            audio_url = ep.get("audio_url", "")

        if audio_url:
            sub(item, "enclosure", url=audio_url, type="audio/mpeg", length="0")

        if ep.get("duration"):
            sub(item, itunes("duration"), ep["duration"])

        if ep.get("episode_image"):
            sub(item, itunes("image"), href=ep["episode_image"])

    return rss

# ── Write output ──────────────────────────────────────────────────────────────

def write_feed(rss):
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    with open(OUTPUT_FILE, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding="utf-8", xml_declaration=False)
    print(f"Wrote {OUTPUT_FILE}")

if __name__ == "__main__":
    schedule = load_schedule()
    episodes = load_episodes()
    rss = build_feed(schedule, episodes)
    write_feed(rss)
    published = sum(
        1 for row in schedule.values()
        if row.get("publish_date") and parse_date(row["publish_date"]).replace(tzinfo=timezone.utc if parse_date(row["publish_date"]).tzinfo is None else parse_date(row["publish_date"]).tzinfo) <= datetime.now(timezone.utc)
    )
    print(f"Published {published} of {len(schedule)} episodes")
