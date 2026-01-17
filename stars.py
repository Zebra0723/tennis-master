from typing import List, Dict
from utils import (
    gdelt_search, google_news_rss_search, safe_get, parse_rss_titles,
    md_link, dedupe_articles, is_low_tier, extract_entities_from_titles,
    guarantee_min_items, polite_sleep
)

STAR_PLAYERS = [
    "Carlos Alcaraz", "Jannik Sinner", "Novak Djokovic", "Daniil Medvedev",
    "Alexander Zverev", "Rafael Nadal",
    "Iga Swiatek", "Aryna Sabalenka", "Coco Gauff", "Elena Rybakina",
]

def _fetch_star_news() -> List[Dict[str, str]]:
    # Primary: GDELT, tightly scoped to 500+ by requiring tour-level terms
    q = "(" + " OR ".join([f'"{p}"' for p in STAR_PLAYERS[:8]]) + ") AND tennis AND (\"ATP 500\" OR \"Masters 1000\" OR \"Grand Slam\" OR \"WTA 500\" OR \"WTA 1000\" OR Wimbledon OR \"Australian Open\" OR \"US Open\" OR \"Roland Garros\")"
    items = gdelt_search(q, max_records=20, hours=48)
    # Filter low-tier noise
    items = [it for it in items if not is_low_tier(it.get("title",""))]
    return items

def _fallback_google_rss() -> List[Dict[str, str]]:
    collected = []
    for p in STAR_PLAYERS[:6]:
        rss = google_news_rss_search(f'{p} tennis ATP 500 OR Masters 1000 OR Grand Slam OR WTA 500 OR WTA 1000')
        xml, err = safe_get(rss)
        if xml and not err:
            for it in parse_rss_titles(xml, limit=2):
                if not is_low_tier(it["title"]):
                    collected.append({"title": it["title"], "url": it["link"]})
        polite_sleep(0.3)
    return collected

def build_stars_section() -> str:
    lines: List[str] = []
    lines.append("## 1) Tennis Stars Brief (ATP/WTA 500+ only)\n")

    items = _fetch_star_news()
    items = dedupe_articles(items, limit=12)

    # Guarantee content by broadening if needed
    def broaden():
        # Broaden by removing the strict 500+ clause but keep “tennis” + star list
        q2 = "(" + " OR ".join([f'"{p}"' for p in STAR_PLAYERS[:8]]) + ") AND tennis"
        return [it for it in gdelt_search(q2, max_records=20, hours=48) if not is_low_tier(it.get("title",""))]

    items = guarantee_min_items(items, min_items=6, broaden_fn=broaden)

    # If still thin, add RSS fallback and dedupe again
    if len(items) < 6:
        rss_items = _fallback_google_rss()
        merged = []
        for it in items:
            merged.append({"title": it.get("title",""), "url": it.get("url","")})
        merged.extend(rss_items)
        items = dedupe_articles(merged, limit=12)

    titles_for_analysis = [it.get("title","") for it in items]
    ents = extract_entities_from_titles(titles_for_analysis)

    lines.append("### What’s happening (last 48h)\n")
    for it in items[:10]:
        title = it.get("title","")
        url = it.get("url","") or it.get("link","")
        lines.append(f"- {md_link(title, url)}")

    lines.append("\n### Analysis\n")
    if ents["players"]:
        lines.append(f"- **Players appearing repeatedly:** {', '.join(ents['players'])}")
    if ents["tournaments"]:
        lines.append(f"- **Tournaments mentioned:** {', '.join(ents['tournaments'])}")
    if ents["tags"]:
        lines.append(f"- **Common storylines:** {', '.join(ents['tags'])}")

    lines.append("\n### What to watch (actionable)\n")
    lines.append("- Watch for withdrawals/injuries affecting draw strength and late-round matchups.")
    lines.append("- Prioritise 500+/1000/Slam context: form here matters; lower-tier noise is filtered out.")
    lines.append("")
    return "\n".join(lines)
