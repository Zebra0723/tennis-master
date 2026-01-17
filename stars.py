from typing import List, Dict
from utils import (
    gdelt_search,
    extract_summary,
    looks_english,
    allowed_source,
    is_low_tier,
    extract_entities,
)

def build_stars_section() -> str:
    lines: List[str] = []
    lines.append("## 1) Tennis Stars Brief (ATP/WTA 500+ only)\n")

    strict_query = (
        'tennis AND ("ATP 500" OR "Masters 1000" OR "Grand Slam" '
        'OR "WTA 500" OR "WTA 1000" OR '
        '"Australian Open" OR Wimbledon OR "US Open" OR "Roland Garros")'
    )

    items = gdelt_search(strict_query, max_records=25, hours=48)

    cleaned: List[Dict[str, str]] = []

    for it in items:
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

    # Fallback: broader elite tennis
    if not cleaned:
        fallback = gdelt_search(
            'tennis AND ("Grand Slam" OR "Masters 1000" OR ATP OR WTA)',
            max_records=20,
            hours=72
        )
        for it in fallback:
            title = it["title"]
            url = it["url"]
            if not looks_english(title) or not allowed_source(url):
                continue
            summary = extract_summary(url)
            if looks_english(summary):
                cleaned.append({"title": title, "url": url, "summary": summary})
            if len(cleaned) >= 4:
                break

    lines.append("### What’s happening\n")
    for c in cleaned:
        lines.append(f"- **{c['title']}**")
        lines.append(f"  - {c['summary']}\n")

    ents = extract_entities([c["title"] for c in cleaned])

    lines.append("### Analysis\n")
    if ents["players"]:
        lines.append(f"- Key players: {', '.join(ents['players'])}")
    if ents["tournaments"]:
        lines.append(f"- Tournaments in focus: {', '.join(ents['tournaments'])}")

    lines.append("\n### Why this matters\n")
    lines.append(
        "- This is elite-tier tennis only (500+/1000/Slams).\n"
        "- Quiet days usually indicate stable draws; intensity rises in later rounds.\n"
        "- Use this to prioritise **which matches and players to follow**.\n"
    )

    return "\n".join(lines)
