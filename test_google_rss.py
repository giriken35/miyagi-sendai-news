import feedparser
import requests

url = "https://news.google.com/rss/search?q=site:kahoku.news&hl=ja&gl=JP&ceid=JP:ja"
resp = requests.get(url)
feed = feedparser.parse(resp.content)
print(f"Kahoku Google News: {len(feed.entries)}")
if feed.entries:
    print(feed.entries[0].title)

url2 = "https://news.google.com/rss/search?q=%E4%BB%99%E5%8F%B0%E3%81%A4%E3%83%BC%E3%81%97%E3%82%93+OR+site:sendai-tushin.jp&hl=ja&gl=JP&ceid=JP:ja"
resp2 = requests.get(url2)
feed2 = feedparser.parse(resp2.content)
print(f"Sendai Tushin Google News: {len(feed2.entries)}")
if feed2.entries:
    print(feed2.entries[0].title)

