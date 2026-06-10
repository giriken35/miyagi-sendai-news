"""
仙台ニュース巡回Webアプリ
Streamlit Cloud 対応・スマホ最適化・電子書籍風ミニマリズムデザイン
"""

import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
import datetime
import concurrent.futures
import re
import time

# ───────────────────────────────────────────────
#  ページ設定（最初に呼ぶ必要がある）
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="仙台ニュース",
    page_icon="📰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ───────────────────────────────────────────────
#  カスタム CSS（Kindle ライクな電子書籍風デザイン）
# ───────────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@300;400;500;700&family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

/* ── リセット & 基盤 ── */
* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #F5F0E8 !important;
    color: #1A1A2E !important;
    font-family: 'Noto Serif JP', 'Hiragino Mincho ProN', Georgia, serif !important;
}

/* ── メインコンテナの幅制限（スマホ最適化） ── */
[data-testid="stAppViewContainer"] > .main .block-container {
    max-width: 680px !important;
    padding: 0.5rem 1rem 3rem 1rem !important;
    margin: 0 auto !important;
}

/* ── ヘッダー ── */
.app-header {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
    color: #E8D5B0 !important;
    padding: 1.5rem 1.25rem 1.2rem;
    border-radius: 0 0 18px 18px;
    margin: -0.5rem -1rem 1.5rem -1rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(26, 26, 46, 0.3);
}
.app-header h1 {
    font-family: 'Noto Serif JP', serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #E8D5B0 !important;
    margin: 0 !important;
    letter-spacing: 0.08em;
    line-height: 1.3;
}
.app-header .subtitle {
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 0.72rem;
    color: #A09070;
    margin-top: 0.3rem;
    letter-spacing: 0.12em;
}
.app-header .update-time {
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 0.68rem;
    color: #7A8FA6;
    margin-top: 0.5rem;
}

/* ── タブ ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #EDE8DC;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
    border-bottom: none !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.08);
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Noto Sans JP', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #5A5A6A !important;
    border-radius: 9px !important;
    padding: 0.45rem 0.6rem !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.2s ease;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #1A1A2E !important;
    color: #E8D5B0 !important;
    box-shadow: 0 2px 8px rgba(26,26,46,0.25) !important;
}
[data-testid="stTabs"] [role="tabpanel"] {
    padding-top: 0.75rem !important;
}

/* ── ニュースカード ── */
.news-card {
    background: #FDFAF4;
    border: 1px solid #E0D8C8;
    border-radius: 12px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.65rem;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    box-shadow: 0 1px 4px rgba(26,26,46,0.06);
    position: relative;
    overflow: hidden;
}
.news-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #0F3460, #1A6B8A);
    border-radius: 3px 0 0 3px;
}
.news-card:hover {
    box-shadow: 0 4px 16px rgba(26,26,46,0.12);
    transform: translateY(-1px);
}

/* ── カード内タイトル ── */
.news-title {
    font-family: 'Noto Serif JP', serif;
    font-size: 0.92rem;
    font-weight: 500;
    color: #1A1A2E;
    line-height: 1.55;
    margin-bottom: 0.35rem;
    letter-spacing: 0.02em;
}

/* ── メタ情報（日時・ソース） ── */
.news-meta {
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 0.65rem;
    color: #8A8070;
    display: flex;
    gap: 0.6rem;
    align-items: center;
    flex-wrap: wrap;
}
.source-badge {
    background: #EDE8DC;
    color: #5A4A3A;
    padding: 0.1rem 0.45rem;
    border-radius: 4px;
    font-size: 0.62rem;
    font-weight: 500;
    white-space: nowrap;
}
.source-badge.kahoku { background: #DDE8F5; color: #1A3A6E; }
.source-badge.tushin { background: #F5E8DD; color: #6E3A1A; }
.source-badge.yahoo  { background: #DDF5E8; color: #1A6E3A; }

/* ── エクスパンダー（本文） ── */
[data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin-top: 0.25rem !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Noto Sans JP', sans-serif !important;
    font-size: 0.75rem !important;
    color: #0F3460 !important;
    font-weight: 500 !important;
    padding: 0.25rem 0 !important;
}
[data-testid="stExpander"] summary:hover {
    color: #1A6B8A !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: #F7F3EC !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    border: 1px solid #E0D8C8 !important;
    margin-top: 0.3rem !important;
}

/* ── 本文テキスト ── */
.article-body {
    font-family: 'Noto Serif JP', serif;
    font-size: 0.88rem;
    line-height: 1.9;
    color: #2A2A3E;
    letter-spacing: 0.03em;
    word-break: break-all;
}
.article-body p { margin-bottom: 0.75rem; }

/* ── 空状態 ── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #8A8070;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 0.85rem;
}

/* ── ローダー ── */
.stSpinner > div { color: #0F3460 !important; }

/* ── ボタン ── */
[data-testid="stButton"] > button {
    font-family: 'Noto Sans JP', sans-serif !important;
    font-size: 0.8rem !important;
    background: #1A1A2E !important;
    color: #E8D5B0 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s ease !important;
}
[data-testid="stButton"] > button:hover {
    background: #0F3460 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 10px rgba(15,52,96,0.3) !important;
}

/* ── リンクボタン ── */
a.open-link-btn {
    display: inline-block;
    margin-top: 0.5rem;
    padding: 0.35rem 0.9rem;
    background: #0F3460;
    color: #E8D5B0 !important;
    text-decoration: none !important;
    border-radius: 6px;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px rgba(15,52,96,0.2);
}
a.open-link-btn:hover {
    background: #1A6B8A;
    box-shadow: 0 3px 10px rgba(15,52,96,0.3);
}

/* ── 区切り線 ── */
hr { border: none; border-top: 1px solid #E0D8C8; margin: 0.5rem 0; }

/* ── Streamlit デフォルト要素の非表示 ── */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── スクロールバー ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #C0B090; border-radius: 2px; }
</style>
"""

# ───────────────────────────────────────────────
#  RSS フィード定義
# ───────────────────────────────────────────────
FEEDS = [
    {
        "name": "河北新報",
        "key": "kahoku",
        "emoji": "📰",
        "urls": [
            "https://kahoku.news/rss/category/news_miyagi.xml",
            "https://kahoku.news/feed/",
            "https://kahoku.news/news/rss/",
        ],
        "fallback_scrape": "https://kahoku.news/",
    },
    {
        "name": "仙台つーしん",
        "key": "tushin",
        "emoji": "🍜",
        "urls": [
            "https://sendai-tushin.jp/feed/",
        ],
        "fallback_scrape": None,
    },
    {
        "name": "Yahoo!宮城",
        "key": "yahoo",
        "emoji": "📡",
        "urls": [
            "https://news.yahoo.co.jp/rss/topics/local/miyagi.xml",
            "https://news.yahoo.co.jp/rss/media/kahoku/articles.xml",
        ],
        "fallback_scrape": None,
    },
]

# ───────────────────────────────────────────────
#  キーワード分類設定
# ───────────────────────────────────────────────
INCIDENT_KEYWORDS = [
    "逮捕", "火災", "事故", "警察", "容疑", "死亡", "負傷", "被害",
    "事件", "犯罪", "捜査", "検挙", "刑事", "窃盗", "詐欺", "暴行",
    "救助", "行方不明", "震度", "地震", "津波", "災害", "台風", "洪水",
]

GOURMET_KEYWORDS = [
    "オープン", "開店", "グルメ", "スイーツ", "カフェ", "レストラン",
    "ラーメン", "寿司", "居酒屋", "ランチ", "ディナー", "フード",
    "閉店", "新店", "牛タン", "ずんだ", "萩の月", "海鮮",
    "パン", "ケーキ", "コーヒー", "ベーカリー", "料理", "食堂",
]

# ───────────────────────────────────────────────
#  ユーティリティ関数
# ───────────────────────────────────────────────

def fetch_rss(feed_info: dict) -> list[dict]:
    """複数の候補 URL を順に試して RSS を取得する。"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
            "Mobile/15E148 Safari/604.1"
        ),
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    for url in feed_info["urls"]:
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200 and len(resp.content) > 200:
                feed = feedparser.parse(resp.content)
                if feed.entries:
                    return _parse_entries(feed.entries, feed_info)
        except Exception:
            continue
    return []


def _parse_entries(entries, feed_info: dict) -> list[dict]:
    """feedparser エントリを統一形式に変換する。"""
    items = []
    for entry in entries[:30]:
        title = entry.get("title", "").strip()
        link  = entry.get("link", "").strip()
        if not title or not link:
            continue

        # 日時パース
        pub = entry.get("published_parsed") or entry.get("updated_parsed")
        if pub:
            try:
                dt = datetime.datetime(*pub[:6], tzinfo=datetime.timezone.utc)
                dt_local = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                date_str = dt_local.strftime("%m/%d %H:%M")
            except Exception:
                date_str = ""
        else:
            date_str = ""

        # 概要
        summary = entry.get("summary", "")
        if summary:
            soup = BeautifulSoup(summary, "html.parser")
            summary = soup.get_text(" ", strip=True)[:120]

        items.append({
            "title":   title,
            "link":    link,
            "date":    date_str,
            "summary": summary,
            "source":  feed_info["name"],
            "source_key": feed_info["key"],
            "emoji":   feed_info["emoji"],
        })
    return items


def fetch_all_feeds() -> list[dict]:
    """全フィードを並列取得してマージ・日時ソートする。"""
    all_items = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_rss, f): f for f in FEEDS}
        for future in concurrent.futures.as_completed(futures, timeout=15):
            try:
                all_items.extend(future.result())
            except Exception:
                pass

    # 重複 URL 除去
    seen = set()
    unique = []
    for item in all_items:
        if item["link"] not in seen:
            seen.add(item["link"])
            unique.append(item)

    # 日付降順ソート（date文字列があるものを優先）
    unique.sort(key=lambda x: x["date"], reverse=True)
    return unique


def classify(item: dict) -> str:
    """タイトルからジャンルを判定する。"""
    title = item["title"]
    # 仙台つーしんは基本的にグルメ・開店
    if item["source_key"] == "tushin":
        return "gourmet"
    for kw in INCIDENT_KEYWORDS:
        if kw in title:
            return "incident"
    for kw in GOURMET_KEYWORDS:
        if kw in title:
            return "gourmet"
    return "general"


def scrape_article(url: str) -> str | None:
    """指定 URL から本文テキストを抽出する（広告・画像除去）。"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
            "Mobile/15E148 Safari/604.1"
        ),
        "Accept-Language": "ja,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = resp.apparent_encoding or "utf-8"
        html = resp.text
    except Exception as e:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # 不要要素を除去
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "figure", "figcaption", "iframe",
                     "noscript", "form", "button", "input",
                     "advertisement", "ads"]):
        tag.decompose()
    for tag in soup.find_all(True, {"class": re.compile(
        r"(ad|ads|advertisement|banner|sidebar|social|share|comment|"
        r"recommend|related|popup|overlay|cookie|breadcrumb|pagination|"
        r"nav|menu|footer|header|widget)", re.I
    )}):
        tag.decompose()

    # 本文候補を探す（article > main > div[class*=content] 順）
    body = None
    for selector in [
        "article",
        '[role="main"]',
        "main",
        '[class*="article-body"]',
        '[class*="article-content"]',
        '[class*="entry-content"]',
        '[class*="post-body"]',
        '[class*="content-body"]',
        '[class*="story-body"]',
        '[class*="article__body"]',
        '[class*="articleBody"]',
        ".content",
        "#content",
    ]:
        body = soup.select_one(selector)
        if body:
            break

    if body is None:
        body = soup.body or soup

    # テキスト抽出
    paragraphs = []
    for p in body.find_all(["p", "h2", "h3", "h4", "li"]):
        text = p.get_text(" ", strip=True)
        # 短すぎる・広告っぽい文は除外
        if len(text) < 15:
            continue
        if any(ng in text for ng in [
            "Cookie", "JavaScript", "ログイン", "会員登録",
            "無断転載", "Copyright", "All Rights Reserved",
            "プライバシー", "利用規約",
        ]):
            continue
        paragraphs.append(text)

    if not paragraphs:
        # フォールバック: 全テキスト
        raw = body.get_text(" ", strip=True)
        return raw[:1500] if raw else None

    return "\n\n".join(paragraphs[:40])


def get_genre_icon(genre: str, source_key: str) -> str:
    icons = {
        "incident": "🚨",
        "gourmet":  "🍽️",
        "general":  "📰",
    }
    if source_key == "tushin":
        return "🛍️"
    return icons.get(genre, "📰")


# ───────────────────────────────────────────────
#  キャッシュ付きデータ取得
# ───────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)  # 5分キャッシュ
def get_news_data():
    """ニュースデータを取得してキャッシュする。"""
    return fetch_all_feeds()


# ───────────────────────────────────────────────
#  UI レンダリング関数
# ───────────────────────────────────────────────

def render_news_card(item: dict, idx: int):
    """1件のニュースカードを描画する。"""
    genre    = classify(item)
    icon     = get_genre_icon(genre, item["source_key"])
    src_key  = item["source_key"]
    badge_cls = f"source-badge {src_key}"

    # カードの外枠
    st.markdown(
        f"""<div class="news-card">
            <div class="news-title">{icon} {item['title']}</div>
            <div class="news-meta">
                <span class="{badge_cls}">{item['source']}</span>
                <span>🕐 {item['date']}</span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # 本文アコーディオン
    exp_key = f"exp_{idx}_{item['link'][:30]}"
    with st.expander("📖 本文を読む", expanded=False):
        col1, col2 = st.columns([5, 1])
        with col1:
            with st.spinner("本文を取得中..."):
                text = scrape_article(item["link"])

        if text and len(text) > 50:
            # 段落ごとに分割して表示
            paras = [p for p in text.split("\n\n") if p.strip()]
            body_html = "".join(f"<p>{p}</p>" for p in paras)
            st.markdown(
                f'<div class="article-body">{body_html}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="article-body">本文の取得に失敗しました。元サイトでご確認ください。</div>',
                unsafe_allow_html=True,
            )

        # 元サイトへのリンク
        st.markdown(
            f'<a href="{item["link"]}" target="_blank" class="open-link-btn">'
            f'🔗 元サイトで読む</a>',
            unsafe_allow_html=True,
        )


def render_tab(items: list[dict], tab_genre: str | None = None):
    """タブ内のニュース一覧を描画する。"""
    if tab_genre == "incident":
        filtered = [it for it in items if classify(it) == "incident"]
    elif tab_genre == "gourmet":
        filtered = [it for it in items if classify(it) == "gourmet"]
    else:
        filtered = items  # 全件

    if not filtered:
        st.markdown(
            '<div class="empty-state">😔 現在ニュースがありません<br>しばらくしてから更新してください</div>',
            unsafe_allow_html=True,
        )
        return

    for i, item in enumerate(filtered[:50]):
        render_news_card(item, i)


# ───────────────────────────────────────────────
#  メイン画面
# ───────────────────────────────────────────────

def main():
    # CSS 適用
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ヘッダー
    now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    st.markdown(
        f"""<div class="app-header">
            <h1>📰 仙台ニュース</h1>
            <div class="subtitle">SENDAI NEWS — 河北新報 / 仙台つーしん / Yahoo!宮城</div>
            <div class="update-time">🕐 {now_jst.strftime('%Y年%m月%d日 %H:%M')} JST</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # データ取得
    with st.spinner("ニュースを取得中..."):
        all_items = get_news_data()

    if not all_items:
        st.error("ニュースの取得に失敗しました。インターネット接続を確認して、ページを更新してください。")
        if st.button("🔄 再読み込み"):
            st.cache_data.clear()
            st.rerun()
        return

    # タブ
    tab_all, tab_incident, tab_gourmet = st.tabs([
        f"📋 すべて ({len(all_items)})",
        f"🚨 事件・事故",
        f"🍽️ グルメ・開店",
    ])

    with tab_all:
        render_tab(all_items, tab_genre=None)

    with tab_incident:
        render_tab(all_items, tab_genre="incident")

    with tab_gourmet:
        render_tab(all_items, tab_genre="gourmet")

    # 更新ボタン（画面下部）
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 ニュースを更新する", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


if __name__ == "__main__":
    main()
