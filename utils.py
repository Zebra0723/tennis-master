import os
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

DEFAULT_UA = "Mozilla/5.0 (TennisMaster/1.0)"

ALLOWED_DOMAINS = (
    "bbc.",
    "theguardian.",
    "nytimes.",
    "espn.",
    "reuters.",
    "apnews.",
    "tennis.com",
    "atptour.com",
    "wtatennis.com",
    "theathletic.",
)

ENGLISH_HINTS = {" the ", " and ", " of ", " to ", " in ", " for "}

LOW_TIER_TERMS = [
    "atp 250", "wta 250", "challenger", "itf", "wta 125", "125"
]

# ---------- Basic helpers ----------

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="minutes")

def ensure_reports_dir():
    os.makedirs("reports", exist_ok=True)

def report_path() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    return f"reports/tennis_report_{ts}.md"

def md_link(title: str, url: str) -> str:
    title = title.replace("[", "(").replace("]", ")")
    return f"[{title}]({url})"

def looks_english(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    ascii_ratio = sum(1 for c in t if ord(c) < 128) / max(len(t), 1)
    return ascii_ratio > 0.9 and any(w in t for w in ENGLISH_HINTS)

def allowed_source(url: str) -> bool:
    return any(d in url.lower() for d in ALLOWED_DOMAINS)

def is_low_tier(title: str) -> bool:
    t = title.lower()
    return any(bad in t for bad in LOW_TIER_TERMS)

# ---------- News fetch (GDELT) ----------

def gdelt_search(query: str, max_records: int = 20, hours: int = 48) -> List[Dict]:
    endpoint = "https://api.gdeltproject.org/api/v2/doc/doc"
    now = datetime.now(timezone.utc)
    start = (now - timedelta(hours=hours)).strftime("%Y%m%d%H%M%S")
    end = now.strftime("%Y%m%d%H%M%S")

    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": max_records,
        "sort": "hybridrel",
        "startdatetime": start,
        "enddatetime": end,
    }

    try:
        r = requests.get(endpoint, params=params, headers={"User-Agent": DEFAULT_UA}, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    out = []
    for art in data.get("articles", []) or []:
        title = (art.get("title") or "").strip()
        url = (art.get("url") or "").strip()
        if title and url:
            out.append({"title": title, "url": url})
    return out

# ---------- Article summarisation ----------

def extract_summary(url: str, max_paragraphs: int = 2) -> str:
    try:
        r = requests.get(url, headers={"User-Agent": DEFAULT_UA}, timeout=20)
        r.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(r.text, "html.parser")
    paras = [
        p.get_text(strip=True)
        for p in soup.find_all("p")
        if len(p.get_text(strip=True)) > 80
    ]
    return " ".join(paras[:max_paragraphs])

# ---------- Simple entity extraction ----------

def extract_entities(titles: List[str]) -> Dict[str, List[str]]:
    players = []
    tournaments = []

    player_keys = [
        "alcaraz","sinner","djokovic","medvedev","zverev","nadal",
        "swiatek","sabalenka","gauff","rybakina"
    ]
    tourney_keys = [
        "australian open","wimbledon","us open","roland garros",
        "masters 1000","atp 500","wta 500","wta 1000"
    ]

    for t in titles:
        tl = t.lower()
        for p in player_keys:
            if p in tl and p.title() not in players:
                players.append(p.title())
        for tr in tourney_keys:
            if tr in tl and tr.title() not in tournaments:
                tournaments.append(tr.title())

    return {"players": players, "tournaments": tournaments} 
