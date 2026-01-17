from typing import List, Dict
from utils import safe_get, google_news_rss_search, parse_rss_titles, md_link, normalize_whitespace, polite_sleep

STAR_PLAYERS = [
    "Carlos Alcaraz", "Jannik Sinner", "Novak Djokovic", "Daniil Medvedev",
    "Alexander Zverev", "Rafael Nadal",
    "Iga Swiatek", "Aryna Sabalenka", "Coco Gauff", "Elena Rybakina",
]

FALLBACK_500PLUS = [
    "ATP 500 / Masters 1000 / Grand Slams",
    "WTA 500 / WTA 1000 / Grand Slams",
]

def _player_news(limit_total: int = 10) -> List[Dict[str, str]]:
    out = []
    for p in STAR_PLAYERS:
        xml, err = safe_get(google_news_rss_search(f"{p} tennis"))
        if xml and not err:
            for it in parse_rss_titles(xml, limit=2):
                out.append(it)
        polite_sleep(0.4)
        if len(out) >= limit_total:
            break
    seen = set()
    uniq = []
    for it in out:
        if it["link"] not in seen:
            seen.add(it["link"])
            uniq.append(it)
    return uniq[:limit_total]

def build_stars_section() -> str:
    lines = []
    lines.append("## 1) Tennis Stars Brief (ATP/WTA 500+ only)\n")
    lines.append("### Tournament Scope\n")
    for x in FALLBACK_500PLUS:
        lines.append(f"- {x}")

    lines.append("\n### Star Headlines\n")
    items = _player_news()
    if not items:
        lines.append("_No headlines available today._")
    else:
        for it in items:
            lines.append(f"- {md_link(it['title'], it['link'])}")

    lines.append("")
    return "\n".join(lines)
