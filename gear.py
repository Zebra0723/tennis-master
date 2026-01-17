from utils import gdelt_search, extract_summary, looks_english, allowed_source

def build_gear_section() -> str:
    lines = []
    lines.append("## 2) Tennis Accessories Radar\n")

    query = (
        '(tennis overgrip OR tennis string OR tennis shoes OR tennis bag) '
        'AND (best OR review)'
    )

    items = gdelt_search(query, max_records=20, hours=72)

    cleaned = []
    for it in items:
        title = it["title"]
        url = it["url"]

        if not looks_english(title) or not allowed_source(url):
            continue

        summary = extract_summary(url)
        if looks_english(summary):
            cleaned.append({"title": title, "summary": summary})
        if len(cleaned) >= 5:
            break

    lines.append("### What’s being recommended\n")
    for c in cleaned:
        lines.append(f"- **{c['title']}**")
        lines.append(f"  - {c['summary']}\n")

    lines.append("### How to use this\n")
    lines.append(
        "- Prioritise repeat-buy items (overgrips, strings).\n"
        "- Only consider shoes/bags if **multiple reviews converge**.\n"
        "- Test one variable at a time for 1–2 weeks.\n"
    )

    return "\n".join(lines)
