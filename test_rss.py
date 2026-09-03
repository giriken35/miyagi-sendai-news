import feedparser
import requests

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

urls = [
    "https://sendai-tushin.jp/feed/",
    "https://kahoku.news/rss/news/",
    "https://news.yahoo.co.jp/rss/topics/local.xml", # Yahoo region
    "https://news.google.com/rss/search?q=%E4%BB%99%E5%8F%B0+OR+%E5%AE%AE%E5%9F%8E&hl=ja&gl=JP&ceid=JP:ja", # Google News Sendai/Miyagi
    "https://assets.sendai-tushin.jp/feed/", # Sometimes subdomains are used
]

for url in urls:
    print(f"Testing {url}")
    try:
        resp = requests.get(url, headers=_REQUEST_HEADERS, timeout=10)
        print(f"Status: {resp.status_code}, Length: {len(resp.content)}")
        if resp.status_code == 200:
            feed = feedparser.parse(resp.content)
            print(f"Parsed entries: {len(feed.entries)}")
            if len(feed.entries) > 0:
                print(f"First entry: {feed.entries[0].title}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)
