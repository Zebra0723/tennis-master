import os
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, List, Dict
import requests
from bs4 import BeautifulSoup

DEFAULT_UA = "Mozilla/5.0 (compatible; TennisMasterBot/1.1)"
REGION = os.getenv("REGION", "UK")

def utc_now_iso_min() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="minutes")

def ensure_reports_dir():
    os.makedirs("reports", exist_ok=True)

def report_path(prefix: str = "tennis_report") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    return f"reports/{prefix}_{ts}.md"

def md_link(title: str, url: str) -> str:
    title = (title or "").replace("[", "(").replace("]", ")").strip()
    return f"[{title}]({url})"

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def polite_sleep(seconds: float):
    time.sleep(seconds)

def safe_get(url: str, params: Optional[dict] = None, timeout: int = 20) -> Tuple[Optional[str], Optional[str]]:
    try:
        r = requests.get(
            url,
            params=params,
            headers={"User-Agent": DEFAULT_UA, "Accept": "*/*"},
            timeout=timeout,
        )
        r.raise_for_status()
        return r.text, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

# --------------------------
# Google News RSS backup
# --------------------------
def google_news_rss_search(query: str, gl: str = "GB", hl: str = "en-GB", ceid: str = "GB:en") -> str:
    from urllib.parse import quote_plus
    q = quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"

def parse_rss_titles(xml_text: str, limit: int = 10) -> List[Dict[str, str]]:
    # Use built-in HTML parser for maximum compatibility in GitHub Actions
    soup = BeautifulSoup(xml_text, "html.parser")
    items = []
    for it in soup.find_all("item")[:limit]:
        title_tag = it.find("title")
        link_tag = it.find("link")
        title = (title_tag.get_text() if title_tag else "").strip()
        link = (link_tag.get_text() if link_tag else "").strip()
        if title and link:
            items.append({"title": title, "link": link})
    return items

# --------------------------
# GDELT (primary, reliable)
# --------------------------
def gdelt_search(query: str, max_records: int = 15, hours: int = 48) -> List[Dict[str, str]]:
    """
    Free JSON news search. Returns list of {title, url, source, datetime}.
    """
    # GDELT Doc 2.1 API
    # We keep it simple and robust.
    endpoint = "https://api.gdeltproject.org/api/v2/doc/doc"

    # last N hours in UTC
    start = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y%m%d%H%M%S")
    end = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": str(max_records),
        "sort": "hybridrel",
        "startdatetime": start,
        "enddatetime": end,
        # English bias (still UK-focused via query wording)
        "format": "json",
    }

    try:
        r = requests.get(endpoint, params=params, headers={"User-Agent": DEFAULT_UA, "Accept": "application/json"}, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        # Fail safely: return empty, caller will fallback
        print(f"[WARN] GDELT failed for query='{query}': {type(e).__name__}: {e}")
        return []

    out: List[Dict[str, str]] = []
    for art in data.get("articles", []) or []:
        title = (art.get("title") or "").strip()
        url = (art.get("url") or "").strip()
        source = (art.get("sourceCountry") or art.get("source") or "").strip()
        dt = (art.get("seendate") or "").strip()
        if title and url:
            out.append({"title": title, "url": url, "source": source, "datetime": dt})
    return out

def dedupe_articles(items: List[Dict[str, str]], limit: int = 15) -> List[Dict[str, str]]:
    seen = set()
    out = []
    for it in items:
        url = it.get("url") or it.get("link")
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(it)
        if len(out) >= limit:
            break
    return out

# --------------------------
# Tennis-specific filtering / analysis helpers
# --------------------------
LOW_TIER_BAD_WORDS = [
    "atp 250", "wta 250", "challenger", "itf", "125", "wta 125"
]

def is_low_tier(text: str) -> bool:
    t = (text or "").lower()
    return any(w in t for w in LOW_TIER_BAD_WORDS)

def extract_entities_from_titles(titles: List[str]) -> Dict[str, List[str]]:
    """
    Very lightweight rule-based extraction (no LLM required).
    """
    players = []
    tournaments = []
    tags = []

    player_keywords = [
        "alcaraz","sinner","djokovic","medvedev","zverev","nadal",
        "swiatek","sabalenka","gauff","rybakina","pegula","jabeur"
    ]
    tourney_keywords = [
        "australian open","roland garros","wimbledon","us open",
        "masters 1000","atp 500","wta 500","wta 1000",
        "indian wells","miami","madrid","rome","cincinnati","shanghai",
        "doha","dubai","rotterdam","queens","halle","tokyo","beijing"
    ]
    tag_keywords = [
        "injury","withdraw","suspension","comeback","seed","draw",
        "upset","final","semi-final","quarterfinal","ranking","coach"
    ]

    for raw in titles:
        t = (raw or "").lower()
        for p in player_keywords:
            if p in t and p not in players:
                players.append(p)
        for tr in tourney_keywords:
            if tr in t and tr not in tournaments:
                tournaments.append(tr)
        for tg in tag_keywords:
            if tg in t and tg not in tags:
                tags.append(tg)

    # normalize for display
    return {
        "players": [p.title() if p != "djokovic" else "Djokovic" for p in players][:8],
        "tournaments": [x.title() for x in tournaments][:8],
        "tags": [x for x in tags][:8],
    }

def guarantee_min_items(items: List[Dict[str, str]], min_items: int, broaden_fn) -> List[Dict[str, str]]:
    """
    If results are too few, broaden the query via broaden_fn() (caller-supplied).
    """
    if len(items) >= min_items:
        return items
    more = broaden_fn()
    merged = dedupe_articles(items + more, limit=max(min_items, 15))
    return merged
