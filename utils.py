import os
import re
import time
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict
import requests
from bs4 import BeautifulSoup

DEFAULT_UA = "Mozilla/5.0 (compatible; TennisMasterBot/1.0)"

def utc_now_iso_min() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="minutes")

def ensure_reports_dir():
    os.makedirs("reports", exist_ok=True)

def report_path(prefix: str = "tennis_report") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    return f"reports/{prefix}_{ts}.md"

def safe_get(url: str, params: Optional[dict] = None, timeout: int = 15) -> Tuple[Optional[str], Optional[str]]:
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

def google_news_rss_search(query: str, gl: str = "GB", hl: str = "en-GB", ceid: str = "GB:en") -> str:
    from urllib.parse import quote_plus
    q = quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"

def parse_rss_titles(xml_text: str, limit: int = 10) -> List[Dict[str, str]]:
    soup = BeautifulSoup(xml_text, "html.parser")
    items = []
    for it in soup.find_all("item")[:limit]:
        title = (it.title.text or "").strip()
        link = (it.link.text or "").strip()
        if title and link:
            items.append({"title": title, "link": link})
    return items

def md_link(title: str, url: str) -> str:
    title = title.replace("[", "(").replace("]", ")")
    return f"[{title}]({url})"

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def polite_sleep(seconds: float):
    time.sleep(seconds)
