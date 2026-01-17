from utils import safe_get, google_news_rss_search, parse_rss_titles, md_link, polite_sleep

GEAR_QUERIES = [
    "best tennis overgrip",
    "best tennis dampener",
    "best tennis string for spin",
    "best tennis shoes",
    "best tennis bag",
]

def build_gear_section() -> str:
    lines = []
    lines.append("## 2) Tennis Accessories Radar\n")
    items = []
    for q in GEAR_QUERIES:
        xml, err = safe_get(google_news_rss_search(q))
        if xml and not err:
            for it in parse_rss_titles(xml, limit=2):
                items.append((q, it["title"], it["link"]))
        polite_sleep(0.4)

    if not items:
        lines.append("_No gear items found today._\n")
        return "\n".join(lines)

    current = None
    for q, title, link in items:
        if q != current:
            current = q
            lines.append(f"### {q}")
        lines.append(f"- {md_link(title, link)}")

    lines.append("")
    return "\n".join(lines)
