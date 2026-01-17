from typing import List, Dict
from utils import (
    gdelt_search, md_link, extract_summary,
    looks_english, allowed_source, is_low_tier,
    extract_entities
)

def build_stars_section() -> str:
    lines: List[str] = []
    lines.append("## 1) Tennis Stars Brief (ATP/WTA 500+ only)\n")

    query = (
        'tennis AND ("ATP 500" OR "Masters 1000" OR "Grand Slam" '
        'OR "WTA 500" OR "WTA 1000" OR '
        '"Australian Open" OR Wimbledon OR "US Open" OR "Roland Garros")'
    )

    raw = gdelt_search(query, max_records=25, hours=48)

    cleaned: List[Dict] = []
    for it in raw:
        title = it["title"]
        url = it["url"]

        if is_low_tier(title):
            continue
        if not looks_english(title):
            continue
        if not allowed_source(url):
            continue

        summary = extract_summary(url)
        if not looks_english(summary):
            continue

        cleaned.append({"title": title, "url": url, "summary": summary})
        if len(cleaned) >= 6:
            break

    titles = [c["title"] for c in cleaned]
    ents = extract_entities(titles)

    lines.append("### What’s happening\n")
    for c in cleaned:
        lines.append(f"- **{c['title']}**")
        lines.append(f"  - {c['summary']}\n")

    lines.append("### Analysis\n")
    if ents["players"]:
        lines.append(f"- Key players: {', '.join(ents['players'])}")
    if ents["tournaments"]:
        lines.append(f"- Tournaments in focus: {', '.join(ents['tournaments'])}")

    lines.append("\n### Why this matters\n")
    lines.append(
        "- Coverage here is exclusively elite-level tennis (500+/1000/Slams).\n"
        "- Repeated mentions usually indicate draw pressure, injury watch, or key form shifts.\n"
        "- Use this to decide **which matches to follow** and **which players’ form to track**.\n"
    )

    return "\n".join(lines)
