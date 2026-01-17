from typing import List, Dict
from utils import gdelt_search, md_link, dedupe_articles, guarantee_min_items

TIP_QUERIES = [
    'tennis (serve OR "second serve") (tip OR drill OR coaching)',
    'tennis (return OR "return of serve") (positioning OR tactic OR tip)',
    'tennis footwork (drill OR coaching OR "movement")',
    'tennis tactics ("high percentage" OR pattern OR strategy)',
    'tennis conditioning ("injury prevention" OR mobility OR strength)',
]

def build_improvement_section() -> str:
    lines: List[str] = []
    lines.append("## 3) Tennis Improvement Tips (practical, actionable)\n")
    lines.append("Sources: recent coaching/tactics/conditioning articles (last 7 days). Goal: one theme/day.\n")

    items: List[Dict[str, str]] = []
    for q in TIP_QUERIES:
        items.extend(gdelt_search(q, max_records=6, hours=168))

    items = dedupe_articles(items, limit=15)

    def broaden():
        return gdelt_search('tennis (coaching OR drill OR tactic OR footwork OR mobility OR strength)', max_records=25, hours=336)

    items = guarantee_min_items(items, min_items=6, broaden_fn=broaden)

    lines.append("### Recent coaching signals\n")
    for it in items[:10]:
        lines.append(f"- {md_link(it.get('title',''), it.get('url',''))}")

    lines.append("\n### Analysis (how to convert tips into progress)\n")
    lines.append("- Don’t collect tips. Convert them into a **single daily focus**.")
    lines.append("- Use a tight loop: **Read 2 mins → pick 1 cue → do 15 mins reps → stop**.")
    lines.append("- Track only one metric: e.g., first-serve % in practice sets, or return depth on 10 consecutive returns.")

    lines.append("\n### Today’s execution template\n")
    lines.append("- Choose one area: **Serve / Return / Footwork / Tactics / Conditioning**")
    lines.append("- Write 1 sentence: “Today I will focus on ________.”")
    lines.append("- Do 15 minutes of reps. End.")
    lines.append("")
    return "\n".join(lines)
