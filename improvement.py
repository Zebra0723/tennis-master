from utils import safe_get, google_news_rss_search, parse_rss_titles, md_link, polite_sleep

TIP_QUERIES = [
    "tennis serve coaching tip",
    "tennis return positioning",
    "tennis footwork drill",
    "tennis tactics patterns",
    "tennis mental toughness",
]

def build_improvement_section() -> str:
    lines = []
    lines.append("## 3) Tennis Improvement Tips\n")
    items = []
    for q in TIP_QUERIES:
        xml, err = safe_get(google_news_rss_search(q))
        if xml and not err:
            for it in parse_rss_titles(xml, limit=2):
                items.append((q, it["title"], it["link"]))
        polite_sleep(0.4)

    if not items:
        lines.append("_No tips found today._\n")
        return "\n".join(lines)

    current = None
    for q, title, link in items[:10]:
        if q != current:
            current = q
            lines.append(f"### {q}")
        lines.append(f"- {md_link(title, link)}")

    lines.append("")
    return "\n".join(lines)
