from typing import List, Dict
from utils import gdelt_search, md_link, dedupe_articles, guarantee_min_items

GEAR_QUERIES = [
    '("tennis overgrip" OR "overgrip") AND (best OR review OR recommended)',
    '("tennis string" OR "poly string") AND (best OR review OR tension)',
    '("tennis shoes") AND (best OR review OR "new model")',
    '("tennis bag") AND (best OR review OR "new")',
    '("tennis dampener" OR "vibration dampener") AND (best OR review)',
]

def build_gear_section() -> str:
    lines: List[str] = []
    lines.append("## 2) Tennis Accessories Radar (best on the market)\n")
    lines.append("Sources: recent articles/reviews (last 48h). Goal: shortlist what’s worth researching/buying.\n")

    all_items: List[Dict[str, str]] = []
    for q in GEAR_QUERIES:
        all_items.extend(gdelt_search(q, max_records=6, hours=72))

    all_items = dedupe_articles(all_items, limit=15)

    def broaden():
        return gdelt_search('tennis (overgrip OR string OR shoes OR bag OR dampener) (review OR best)', max_records=20, hours=168)

    all_items = guarantee_min_items(all_items, min_items=6, broaden_fn=broaden)

    lines.append("### Recent “best / review” signals\n")
    for it in all_items[:10]:
        lines.append(f"- {md_link(it.get('title',''), it.get('url',''))}")

    lines.append("\n### Analysis (how to use this)\n")
    lines.append("- Focus on **repeat-buy accessories** first (overgrips, strings). They drive recurring revenue and quick testing cycles.")
    lines.append("- Treat shoes/bags as **higher-friction** purchases—buy only if multiple reputable sources converge.")
    lines.append("- Build a shortlist of 2–3 candidates per category and test one variable at a time (e.g., overgrip tackiness vs durability).")

    lines.append("\n### Today’s recommendation\n")
    lines.append("- Pick **one** category to research (e.g., overgrips). Open the top 2 links, extract the exact product names, and compare price/availability in the UK.")
    lines.append("")
    return "\n".join(lines)
