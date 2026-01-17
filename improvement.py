from utils import gdelt_search, extract_summary, looks_english, allowed_source

def build_improvement_section() -> str:
    lines = []
    lines.append("## 3) Tennis Improvement Focus\n")

    query = (
        'tennis (serve OR return OR footwork OR tactics OR conditioning) '
        'AND (coaching OR drill OR tip)'
    )

    items = gdelt_search(query, max_records=20, hours=168)

    cleaned = []
    for it in items:
        title = it["title"]
        url = it["url"]

        if not looks_english(title) or not allowed_source(url):
            continue

        summary = extract_summary(url)
        if looks_english(summary):
            cleaned.append({"title": title, "summary": summary})
        if len(cleaned) >= 4:
            break

    lines.append("### Today’s learning\n")
    for c in cleaned:
        lines.append(f"- **{c['title']}**")
        lines.append(f"  - {c['summary']}\n")

    lines.append("### Execution rule\n")
    lines.append(
        "- Pick **one** idea.\n"
        "- Do **15 minutes** of focused reps.\n"
        "- Stop. Consistency beats volume.\n"
    )

    return "\n".join(lines)
