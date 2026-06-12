import json
import datetime
import concurrent.futures
import re
import difflib
import feedparser
import requests
from bs4 import BeautifulSoup

# ───────────────────────────────────────────────
#  RSS フィード定義
# ───────────────────────────────────────────────
FEEDS = [
    {
        "name": "仙台つーしん",
        "key": "tushin",
        "emoji": "🍜",
        "urls": [
            "https://sendai-tushin.jp/feed/",
            "https://news.google.com/rss/search?q=site:sendai-tushin.jp&hl=ja&gl=JP&ceid=JP:ja",
        ],
    },
    {
        "name": "河北新報",
        "key": "kahoku",
        "emoji": "📰",
        "urls": [
            "https://news.google.com/rss/search?q=site:kahoku.news&hl=ja&gl=JP&ceid=JP:ja",
            "https://kahoku.news/feed/",
        ],
    },
    {
        "name": "NHK東北",
        "key": "nhk",
        "emoji": "📡",
        "urls": [
            "https://news.google.com/rss/search?q=NHK+%E5%AE%AE%E5%9F%8E+OR+%E4%BB%99%E5%8F%B0&hl=ja&gl=JP&ceid=JP:ja",
            "https://www3.nhk.or.jp/rss/news/cat0.xml",
        ],
    },
    {
        "name": "Yahoo!ニュース",
        "key": "yahoo",
        "emoji": "🗞️",
        "urls": [
            "https://news.google.com/rss/search?q=site:news.yahoo.co.jp+%E5%AE%AE%E5%9F%8E+OR+%E4%BB%99%E5%8F%B0&hl=ja&gl=JP&ceid=JP:ja",
            "https://news.yahoo.co.jp/rss/topics/domestic.xml",
        ],
    },
    {
        "name": "TBC東北放送",
        "key": "tbc",
        "emoji": "📺",
        "urls": ["https://news.yahoo.co.jp/rss/media/tbcv/all.xml"],
    },
    {
        "name": "仙台放送",
        "key": "ox",
        "emoji": "📺",
        "urls": ["https://news.yahoo.co.jp/rss/media/oxv/all.xml"],
    },
    {
        "name": "ミヤギテレビ",
        "key": "mmt",
        "emoji": "📺",
        "urls": ["https://news.yahoo.co.jp/rss/media/mmt/all.xml"],
    },
    {
        "name": "khb東日本放送",
        "key": "khb",
        "emoji": "📺",
        "urls": ["https://news.yahoo.co.jp/rss/media/khbv/all.xml"],
    },
]

# 取得上限：各媒体ごとの最新件数
PER_SOURCE_LIMIT: int = 100
# 期間制限：現在から何日前までの記事を許可するか
DAYS_LIMIT: int = 60

# 宮城・仙台関連キーワード
MIYAGI_KEYWORDS: list[str] = [
    "仙台", "宮城",
    "青葉区", "宮城野区", "若林区", "太白区", "泉区",
]

_UA_BROWSER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_REQUEST_HEADERS = {
    "User-Agent": _UA_BROWSER,
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "ja,en;q=0.9",
    "Cache-Control": "no-cache",
}

def fetch_rss(feed_info: dict) -> tuple[list[dict], str]:
    last_error = ""

    for url in feed_info["urls"]:
        # feedparser
        try:
            feed = feedparser.parse(
                url,
                agent=_UA_BROWSER,
                request_headers=_REQUEST_HEADERS,
            )
            if feed.entries:
                return _parse_entries(feed.entries, feed_info), url
        except Exception as e:
            last_error = f"feedparser direct [{url}]: {e}"

        # requests -> feedparser
        try:
            resp = requests.get(
                url,
                headers=_REQUEST_HEADERS,
                timeout=12,
                allow_redirects=True,
                verify=True,
            )
            if resp.status_code == 200 and len(resp.content) > 300:
                resp.encoding = resp.apparent_encoding or "utf-8"
                feed = feedparser.parse(resp.content)
                if feed.entries:
                    return _parse_entries(feed.entries, feed_info), url
        except requests.exceptions.SSLError:
            try:
                resp = requests.get(
                    url,
                    headers=_REQUEST_HEADERS,
                    timeout=12,
                    allow_redirects=True,
                    verify=False,
                )
                if resp.status_code == 200 and len(resp.content) > 300:
                    resp.encoding = resp.apparent_encoding or "utf-8"
                    feed = feedparser.parse(resp.content)
                    if feed.entries:
                        return _parse_entries(feed.entries, feed_info), url
            except Exception as e:
                last_error = f"requests(no-verify) [{url}]: {e}"
        except Exception as e:
            last_error = f"requests [{url}]: {e}"
            continue

    return [], last_error

def _parse_entries(entries, feed_info: dict) -> list[dict]:
    items = []
    for entry in entries[:50]:
        title = entry.get("title", "").strip()
        link  = entry.get("link", "").strip()
        if not title or not link:
            continue

        pub = entry.get("published_parsed") or entry.get("updated_parsed")
        pub_ts: float = 0.0
        date_str: str = ""
        if pub:
            try:
                dt_utc = datetime.datetime(*pub[:6], tzinfo=datetime.timezone.utc)
                dt_jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                pub_ts  = dt_utc.timestamp()
                date_str = dt_jst.strftime("%m/%d %H:%M")
            except Exception:
                pass

        summary = entry.get("summary", "")
        if summary:
            try:
                soup = BeautifulSoup(summary, "html.parser")
                summary = soup.get_text(" ", strip=True)[:300]
                
                t_clean = title.replace(" ", "").replace("　", "")
                s_clean = summary.replace(" ", "").replace("　", "")
                if len(t_clean) >= 10 and s_clean.startswith(t_clean[:10]):
                    if len(s_clean) <= len(t_clean) + 25:
                        summary = ""
            except Exception:
                summary = ""

        items.append({
            "title":      title,
            "link":       link,
            "date":       date_str,
            "pub_ts":     pub_ts,
            "summary":    summary,
            "source":     feed_info["name"],
            "source_key": feed_info["key"],
            "emoji":      feed_info["emoji"],
        })
    return items

def fetch_all_feeds() -> tuple[list[dict], dict]:
    all_items: list[dict] = []
    debug_info: dict = {}

    futures_map: dict = {}
    try:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        for f in FEEDS:
            fut = executor.submit(fetch_rss, f)
            futures_map[fut] = f["name"]

        done, not_done = concurrent.futures.wait(
            futures_map.keys(),
            timeout=25,
            return_when=concurrent.futures.ALL_COMPLETED,
        )
        executor.shutdown(wait=False)

        for fut in done:
            feed_name = futures_map[fut]
            try:
                items, info = fut.result(timeout=1)
                all_items.extend(items)
                debug_info[feed_name] = f"✅ {len(items)}件 ({info})"
            except Exception as e:
                debug_info[feed_name] = f"❌ {e}"

        for fut in not_done:
            feed_name = futures_map[fut]
            debug_info[feed_name] = "⏱️ タイムアウト"
            fut.cancel()

    except Exception as e:
        debug_info["system"] = f"並列取得エラー: {e}"

    seen_links: set = set()
    seen_titles: list[str] = []
    unique: list[dict] = []
    for item in all_items:
        norm_title = re.sub(r'（.*?）|\(.*?\)| - Yahoo!ニュース', '', item["title"])
        norm_title = re.sub(r'\s+', '', norm_title)
        
        is_duplicate = False
        if item["link"] in seen_links:
            is_duplicate = True
        else:
            for st_title in seen_titles:
                if difflib.SequenceMatcher(None, norm_title, st_title).ratio() > 0.85:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            seen_links.add(item["link"])
            seen_titles.append(norm_title)
            unique.append(item)

    now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
    cutoff_ts = now_ts - DAYS_LIMIT * 86400

    after_time: list[dict] = [
        it for it in unique
        if it["pub_ts"] == 0.0 or it["pub_ts"] >= cutoff_ts
    ]

    after_region: list[dict] = []
    for it in after_time:
        if it["source_key"] == "tushin":
            after_region.append(it)
        elif any(kw in it["title"] + it["summary"] for kw in MIYAGI_KEYWORDS):
            after_region.append(it)

    from collections import defaultdict
    source_buckets: dict[str, list[dict]] = defaultdict(list)
    for it in after_region:
        source_buckets[it["source_key"]].append(it)

    after_cap: list[dict] = []
    for src_key, src_items in source_buckets.items():
        sorted_src = sorted(src_items, key=lambda x: x["pub_ts"], reverse=True)
        after_cap.extend(sorted_src[:PER_SOURCE_LIMIT])

    after_cap.sort(key=lambda x: (x["pub_ts"], x["date"]), reverse=True)

    return after_cap, debug_info

if __name__ == "__main__":
    print("ニュースを取得中...")
    items, debug = fetch_all_feeds()
    
    # news_data.json に保存
    output_data = {
        "fetched_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S"),
        "items": items,
        "debug_info": debug
    }
    
    with open("news_data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"取得完了: {len(items)}件保存しました。")
    for k, v in debug.items():
        print(f"  {k}: {v}")
