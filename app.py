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
import difflib

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
    gap: 4px;
    border-bottom: none !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.08);
    flex-wrap: wrap !important;
    justify-content: flex-start !important;
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
    flex-grow: 0 !important;
    justify-content: center !important;
}
/* PCのみ（画面幅768px以上）：1段あたり最大6ジャンルになるよう幅を制限 */
@media (min-width: 768px) {
    [data-testid="stTabs"] [role="tab"] {
        flex: 1 1 calc((100% - 20px) / 6) !important;
        max-width: calc((100% - 20px) / 6) !important;
        padding: 0.45rem 0.2rem !important;
    }
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

/* ── カードのレイアウトと日付ボックス ── */
.news-card-inner {
    display: flex;
    gap: 0.8rem;
    align-items: center;
}
.news-date-box {
    flex-shrink: 0;
    text-align: center;
    background: #F5F0E6;
    padding: 0.55rem 0.65rem;
    border-radius: 8px;
    color: #5A4A3A;
    min-width: 4.6rem;
    font-family: 'Noto Sans JP', sans-serif;
    border: 1px solid #EAE3D5;
}
.news-date-day {
    font-size: 1.1rem;
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.news-date-time {
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 0.2rem;
    color: #8A8070;
}
.news-content-area {
    flex-grow: 1;
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
#  ※ urls は上から順に試行し、最初に成功したものを使用する
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

# ───────────────────────────────────────────────
#  キーワード分類設定
# ───────────────────────────────────────────────
CRIME_KEYWORDS = [
    "逮捕", "警察", "容疑", "被害", "事件", "犯罪", "捜査", "検挙", "刑事",
    "窃盗", "詐欺", "暴行", "強盗", "殺人", "送検", "書類送検",
    "殺害", "罪", "被告", "判決", "実刑", "控訴", "棄却", "侵入", "裁判", "地裁", "高裁", "泥棒", "起訴",
    "いじめ", "イジメ", "体罰", "不登校", "暴言", "虐待", "ハラスメント", "セクハラ", "パワハラ", "不祥事", "隠蔽", "恐喝", "脅迫",
    "不審者", "声かけ", "つきまとい", "談合", "横領", "申告漏れ", "無申告", "脱税", "違反", "流出", "陳謝", "謝罪", "損害", "賠償"
]

ACCIDENT_KEYWORDS = [
    "事故", "火災", "死亡", "負傷", "救助", "行方不明", "衝突", "転落", "炎上",
    "災害", "洪水"
]

EARTHQUAKE_KEYWORDS = [
    "震度", "地震", "津波", "余震", "マグニチュード", "揺れ",
    "震災", "被災", "復興", "避難", "防災", "遺構", "慰霊", "伝承", "大川小学校", "防災無線", "仮設", "液状化", "断層", "活断層", "備蓄"
]

SPORTS_KEYWORDS = [
    "スポーツ", "野球", "プロ野球", "高校野球", "サッカー", "バスケ", "バスケット", "Bリーグ", "楽天", "イーグルス",
    "ベガルタ", "89ERS", "８９ＥＲＳ", "ナイナーズ", "試合", "大会", "優勝", "選手", "監督", "五輪", "オリンピック",
    "巨人", "マウンド", "降板", "ホームラン", "ドラフト", "移籍", "退団", "入団", "獲得", "復帰", "シーズン",
    "相撲", "大相撲", "力士", "部屋", "合宿", "はっけよい", "横綱", "親方"
]

GOURMET_KEYWORDS = [
    "オープン", "開店", "グルメ", "スイーツ", "カフェ", "レストラン",
    "ラーメン", "寿司", "居酒屋", "ランチ", "ディナー", "フード",
    "閉店", "新店", "牛タン", "ずんだ", "萩の月", "海鮮",
    "パン", "ケーキ", "コーヒー", "ベーカリー", "料理", "食堂",
    "移転", "店舗", "飲食店", "弁当", "焼肉", "そば", "うどん"
]

REALESTATE_KEYWORDS = [
    "不動産", "マンション", "アパート", "住宅", "地価", "分譲",
    "再開発", "ビル", "新築", "賃貸", "物件", "商業施設", "タワマン",
    "開発", "建設", "着工", "竣工", "跡地"
]

BEAR_KEYWORDS = [
    "熊", "クマ", "ツキノワグマ", "ヒグマ", "出没", "目撃"
]

EVENT_KEYWORDS = [
    "イベント", "フェス", "祭り", "まつり", "花火", "ライブ", "コンサート",
    "開催", "大会", "マルシェ", "フェスティバル", "展示", "展覧会", "イルミネーション"
]

TRAFFIC_KEYWORDS = [
    "交通", "渋滞", "通行止め", "電車", "遅延", "運休", "新幹線",
    "バス", "フライト", "航空", "地下鉄", "JR", "運転見合わせ", "ダイヤ乱れ"
]

# ── 宮城県・仙台市 地域キーワード（厳格化版・定義済み） ──
POLITICS_KEYWORDS = [
    "政治", "選挙", "市長", "県知事", "知事", "議会", "市議会", "県議会", "議員", "市議", "県議", "町議", "村議", "立候補", "投票", "当選", "落選", "辞職", "公約", "市政", "県政", "自民", "立憲", "公明", "共産", "維新"
]

BUSINESS_KEYWORDS = [
    "ビジネス", "経済", "企業", "会社", "社長", "経営", "倒産", "破産", "業績", "決算", "株式", "株価", "上場", "投資", "出資", "買収", "提携", "合併", "売上", "利益", "赤字", "黒字", "事業", "創業", "ベンチャー", "工場", "営業", "雇用", "就職", "採用", "労働", "賃上げ", "給与", "経済効果"
]

MEDICAL_KEYWORDS = [
    "医療", "病院", "医師", "看護師", "患者", "感染", "コロナ", "インフルエンザ", "ワクチン", "治療", "手術", "病気", "保健所", "健康", "クリニック", "診療",
    "検診", "がん", "ガン", "救急", "救命", "薬", "処方", "小児科", "内科", "外科", "歯科", "産婦人科", "リハビリ", "介護", "福祉施設", "社会福祉", "症状", "診断", "人間ドック", "保健", "ウィルス", "ウイルス", "熱中症"
]

LIFE_KEYWORDS = [
    "生活", "暮らし", "子育て", "教育", "学校", "保育園", "幼稚園", "児童", "生徒", "給食", "スーパー", "買い物", "値上げ", "補助金", "支援金", "ゴミ", "水道",
    "ごみ", "資源", "リサイクル", "育児", "家計", "節約", "年金", "税金", "給付金", "マイナンバー", "コンビニ", "物価", "電気代", "ガス", "公共料金", "市役所", "区役所", "公園", "停電", "断水", "通勤", "通学",
    "お中元", "お歳暮", "贈り物", "ギフト", "商戦", "デパート", "百貨店", "物産展",
    "ガソリン", "灯油", "燃料", "値下がり", "給油"
]

WEATHER_KEYWORDS = [
    "天気", "気象", "気温", "猛暑", "寒波", "雨", "雪", "注意報", "警報", "台風", "梅雨", "雷", "ひょう", "降水", "晴れ", "曇り", "夏日", "真夏日", "猛暑日", "冬日", "真冬日", "積雪", "暴風", "強風", "大雨", "大雪", "気圧", "前線", "降雨", "豪雨", "天気予報", "乾燥"
]
# この7語のいずれかがタイトルまたは概要に含まれる記事のみ表示する
MIYAGI_KEYWORDS: list[str] = [
    "仙台", "宮城",
    "青葉区", "宮城野区", "若林区", "太白区", "泉区",
]

# 取得上限：各媒体ごとの最新件数
PER_SOURCE_LIMIT: int = 100
# 期間制限：現在から何日前までの記事を許可するか
DAYS_LIMIT: int = 60

# ───────────────────────────────────────────────
#  ユーティリティ関数
# ───────────────────────────────────────────────

# Streamlit Cloud / 一般サーバー向け User-Agent
_UA_BROWSER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_UA_BOT = "FeedFetcher/1.0 (+https://streamlit.io)"

_REQUEST_HEADERS = {
    "User-Agent": _UA_BROWSER,
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "ja,en;q=0.9",
    "Cache-Control": "no-cache",
}


def fetch_rss(feed_info: dict) -> tuple[list[dict], str]:
    """複数の候補 URL を順に試して RSS を取得する。
    戻り値: (items_list, '成功したURL or 空文字')
    """
    last_error = ""

    for url in feed_info["urls"]:
        # ── 方法1: feedparser に直接URLを渡す（内部で HTTP 取得） ──
        try:
            feed = feedparser.parse(
                url,
                agent=_UA_BROWSER,
                request_headers=_REQUEST_HEADERS,
            )
            # bozo=True でも entries があれば使う（軽微なXMLエラーは許容）
            if feed.entries:
                return _parse_entries(feed.entries, feed_info), url
        except Exception as e:
            last_error = f"feedparser direct [{url}]: {e}"

        # ── 方法2: requests で取得 → feedparser でパース ──
        try:
            resp = requests.get(
                url,
                headers=_REQUEST_HEADERS,
                timeout=12,
                allow_redirects=True,
                verify=True,
            )
            if resp.status_code == 200 and len(resp.content) > 300:
                # 文字コードを明示してからパース
                resp.encoding = resp.apparent_encoding or "utf-8"
                feed = feedparser.parse(resp.content)
                if feed.entries:
                    return _parse_entries(feed.entries, feed_info), url
        except requests.exceptions.SSLError:
            # SSL エラーの場合は verify=False で再試行
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
    """feedparser エントリを統一形式に変換する。"""
    items = []
    for entry in entries[:50]:  # 上限を増やしてからどうせフィルタにかける
        title = entry.get("title", "").strip()
        link  = entry.get("link", "").strip()
        if not title or not link:
            continue

        # 日時パース ─ 表示用文字列と Unixタイムスタンプの両方を保持
        pub = entry.get("published_parsed") or entry.get("updated_parsed")
        pub_ts: float = 0.0  # 0 = 不明（期間フィルタで通過扱い）
        date_str: str = ""
        if pub:
            try:
                dt_utc = datetime.datetime(*pub[:6], tzinfo=datetime.timezone.utc)
                dt_jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                pub_ts  = dt_utc.timestamp()
                date_str = dt_jst.strftime("%m/%d %H:%M")
            except Exception:
                pass

        # 概要（HTMLタグ除去）
        summary = entry.get("summary", "")
        if summary:
            try:
                soup = BeautifulSoup(summary, "html.parser")
                summary = soup.get_text(" ", strip=True)[:300]
                
                # タイトルとほぼ同じ内容（重複）なら概要を消去する
                t_clean = title.replace(" ", "").replace("　", "")
                s_clean = summary.replace(" ", "").replace("　", "")
                if len(t_clean) >= 10 and s_clean.startswith(t_clean[:10]):
                    # 概要がタイトルより極端に長くない（＋25文字以内）なら重複とみなす
                    if len(s_clean) <= len(t_clean) + 25:
                        summary = ""
            except Exception:
                summary = ""

        items.append({
            "title":      title,
            "link":       link,
            "date":       date_str,
            "pub_ts":     pub_ts,    # 期間フィルタ・ソート用 Unixタイムスタンプ
            "summary":    summary,
            "source":     feed_info["name"],
            "source_key": feed_info["key"],
            "emoji":      feed_info["emoji"],
        })
    return items


def fetch_all_feeds() -> tuple[list[dict], dict]:
    """全フィードを並列取得してマージ・日時ソートする。
    戻り値: (items_list, debug_info_dict)
    """
    all_items: list[dict] = []
    debug_info: dict = {}  # フィード名 -> 成功URL or エラー文字列

    futures_map: dict = {}
    try:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        for f in FEEDS:
            fut = executor.submit(fetch_rss, f)
            futures_map[fut] = f["name"]

        # タイムアウトを長めに設定し、TimeoutError を明示的に捕捉する
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

    # 重複 URL・タイトル除去
    seen_links: set = set()
    seen_titles: list[str] = []
    unique: list[dict] = []
    for item in all_items:
        # メディア名や空白を削って実質的なタイトルで重複チェック
        norm_title = re.sub(r'（.*?）|\(.*?\)| - Yahoo!ニュース', '', item["title"])
        norm_title = re.sub(r'\s+', '', norm_title)
        
        # URL完全一致、またはタイトルの類似度が85%以上なら重複とみなす
        is_duplicate = False
        if item["link"] in seen_links:
            is_duplicate = True
        else:
            for st_title in seen_titles:
                # SequenceMatcherで「が」「を」などの助詞抜けによる表記揺れを吸収
                if difflib.SequenceMatcher(None, norm_title, st_title).ratio() > 0.85:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            seen_links.add(item["link"])
            seen_titles.append(norm_title)
            unique.append(item)

    # ───────────────────────────────────────────────
    #  3段階フィルタリング
    # ───────────────────────────────────────────────

    now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
    cutoff_ts = now_ts - DAYS_LIMIT * 86400  # 30日 × 86400秒

    # ステップ1: 期間フィルタ（30日以内、pub_ts=0 は不明として通過）
    after_time: list[dict] = [
        it for it in unique
        if it["pub_ts"] == 0.0 or it["pub_ts"] >= cutoff_ts
    ]
    debug_info["期間フィルタ"] = (
        f"✅ {len(unique)}件 → {len(after_time)}件"
        f"（{DAYS_LIMIT}日以上を除外: {len(unique)-len(after_time)}件）"
    )

    # ステップ2: 地域フィルタ（宮城/仙台関連キーワード）
    # 仙台つーしん（tushin）は全記事が地域情報なので常に通過
    after_region: list[dict] = []
    for it in after_time:
        if it["source_key"] == "tushin":
            after_region.append(it)
        elif any(kw in it["title"] + it["summary"] for kw in MIYAGI_KEYWORDS):
            after_region.append(it)
    debug_info["地域フィルタ"] = (
        f"✅ {len(after_time)}件 → {len(after_region)}件"
        f"（除外: {len(after_time)-len(after_region)}件 / "
        f"キーワード: {', '.join(MIYAGI_KEYWORDS)}）"
    )

    # ステップ3: 媒体ごとに最新{PER_SOURCE_LIMIT}件に限定
    # pub_ts 降順（新しい順）で並び替えて上位{PER_SOURCE_LIMIT}件だけ残す
    from collections import defaultdict
    source_buckets: dict[str, list[dict]] = defaultdict(list)
    for it in after_region:
        source_buckets[it["source_key"]].append(it)

    after_cap: list[dict] = []
    for src_key, src_items in source_buckets.items():
        # pub_ts 降順ソート→上位PER_SOURCE_LIMIT件
        sorted_src = sorted(src_items, key=lambda x: x["pub_ts"], reverse=True)
        after_cap.extend(sorted_src[:PER_SOURCE_LIMIT])
        src_name = sorted_src[0]["source"] if sorted_src else src_key
        debug_info[f"上限({src_name})"] = (
            f"✅ {len(src_items)}件 → {min(len(src_items), PER_SOURCE_LIMIT)}件"
        )

    # 全媒体を合流して日付降順ソート
    after_cap.sort(key=lambda x: (x["pub_ts"], x["date"]), reverse=True)
    debug_info["合計"] = f"✅ 全{len(after_cap)}件を表示"

    return after_cap, debug_info


def classify(item: dict) -> str:
    """タイトルからジャンルを判定する。"""
    title = item["title"]
    
    # --- ジャンルごとの個別除外ルール ---
    exclude_accident = any(kw in title for kw in ["訓練", "想定", "演習"])
    exclude_crime = any(kw in title for kw in ["啓発", "キャンペーン", "パトロール", "交通安全"])

    # 仙台つーしんは基本的にグルメ・開店が多いが、熊や不動産も混ざるので順序に注意
    for kw in BEAR_KEYWORDS:
        if kw in title:
            return "bear"
    for kw in SPORTS_KEYWORDS:
        if kw in title:
            return "sports"
    for kw in EVENT_KEYWORDS:
        if kw in title:
            return "event"
    for kw in TRAFFIC_KEYWORDS:
        if kw in title:
            return "traffic"
            
    for kw in EARTHQUAKE_KEYWORDS:
        if kw in title:
            return "earthquake"
            
    if not exclude_accident:
        for kw in ACCIDENT_KEYWORDS:
            if kw in title:
                return "accident"
                
    if not exclude_crime:
        for kw in CRIME_KEYWORDS:
            if kw in title:
                return "crime"

    for kw in POLITICS_KEYWORDS:
        if kw in title:
            return "politics"
            
    exclude_business = any(kw in title for kw in ["仙台つーしん", "ラーメン", "らーめん", "らぁ", "麺", "カフェ", "スイーツ", "レストラン", "居酒屋", "寿司", "食堂", "パン", "ケーキ", "グルメ", "飲食店", "牛タン", "ずんだ", "ベーカリー", "弁当", "焼肉", "そば", "うどん", "メニュー", "テイクアウト", "ヤクルト"])
    if not exclude_business:
        for kw in BUSINESS_KEYWORDS:
            if kw in title:
                return "business"
            
    exclude_medical = any(kw in title for kw in ["生活保護"])
    if not exclude_medical:
        for kw in MEDICAL_KEYWORDS:
            if kw in title:
                return "medical"
                
    for kw in WEATHER_KEYWORDS:
        if kw in title:
            return "weather"
    for kw in LIFE_KEYWORDS:
        if kw in title:
            return "life"
    for kw in REALESTATE_KEYWORDS:
        if kw in title:
            return "realestate"
    for kw in GOURMET_KEYWORDS:
        if kw in title:
            return "gourmet"
            
    if item["source_key"] == "tushin":
        return "gourmet"
        
    return "general"


def get_genre_icon(genre: str, source_key: str) -> str:
    icons = {
        "crime":      "🚨",
        "accident":   "💥",
        "earthquake": "⚠️",
        "gourmet":    "🍽️",
        "realestate": "🏢",
        "bear":       "🐻",
        "event":      "🎪",
        "traffic":    "🚃",
        "sports":     "⚽",
        "politics":   "🏛️",
        "medical":    "🏥",
        "life":       "🏠",
        "general":    "📰",
    }
    # 仙台つーしんで一般記事に分類された場合は買い物アイコンを優先
    if source_key == "tushin" and genre == "general":
        return "🛍️"
    return icons.get(genre, "📰")


# ───────────────────────────────────────────────
#  キャッシュ付きデータ取得
# ───────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)  # 5分キャッシュ
def get_news_data() -> tuple[list[dict], dict]:
    """ニュースデータを取得してキャッシュする。"""
    try:
        return fetch_all_feeds()
    except Exception as e:
        return [], {"system": f"致命的エラー: {e}"}


# ───────────────────────────────────────────────
#  UI レンダリング関数
# ───────────────────────────────────────────────

def render_news_card(item: dict, idx: int):
    """1件のニュースカードを描画する。"""
    genre    = classify(item)
    icon     = get_genre_icon(genre, item["source_key"])
    src_key  = item["source_key"]
    badge_cls = f"source-badge {src_key}"

    date_parts = item.get('date', '').split(" ")
    if len(date_parts) >= 2:
        day_str = date_parts[0]
        if day_str.startswith("0"): 
            day_str = day_str[1:] # 06/10 -> 6/10
        time_str = date_parts[1]
    else:
        day_str = "--/--"
        time_str = "--:--"

    # カードの外枠
    st.markdown(
        f"""<div class="news-card">
            <div class="news-card-inner">
                <div class="news-date-box">
                    <div class="news-date-day">{day_str}</div>
                    <div class="news-date-time">{time_str}</div>
                </div>
                <div class="news-content-area">
                    <div class="news-title">{icon} {item['title']}</div>
                    <div class="news-meta" style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                        <div style="display: flex; gap: 0.6rem; align-items: center; flex-wrap: wrap;">
                            <span class="{badge_cls}">{item['source']}</span>
                        </div>
                        <a href="{item['link']}" target="_blank" class="open-link-btn" style="margin-top: 0; padding: 0.25rem 0.6rem; font-size: 0.65rem; white-space: nowrap;">🔗 続きを読む</a>
                    </div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_tab(items: list[dict], tab_genre: str | None = None):
    """タブ内のニュース一覧を描画する。"""
    key_suffix = tab_genre if tab_genre else "all"
    
    # 検索窓（ジャンルタブの下）
    search_query = st.text_input(
        "🔍 全記事からキーワードで検索",
        value="",
        key=f"search_{key_suffix}",
        placeholder="例: 泉区、お祭り、火事..."
    )

    if search_query:
        # 検索時はジャンルを無視して全記事から探す（全体検索の維持）
        sq = search_query.lower()
        filtered = [it for it in items if sq in it.get("title", "").lower() or sq in it.get("summary", "").lower()]
        
        # 戻るボタン
        if st.button("⬅️ 検索をクリアして前の画面に戻る", key=f"back_{key_suffix}"):
            st.session_state[f"search_{key_suffix}"] = ""
            st.rerun()
            
        st.markdown(f"**「{search_query}」の検索結果: {len(filtered)}件**")
    else:
        # 通常時はタブのジャンルのみ表示
        if tab_genre == "crime":
            filtered = [it for it in items if classify(it) == "crime"]
    elif tab_genre == "accident":
        filtered = [it for it in items if classify(it) == "accident"]
    elif tab_genre == "earthquake":
        filtered = [it for it in items if classify(it) == "earthquake"]
    elif tab_genre == "gourmet":
        filtered = [it for it in items if classify(it) == "gourmet"]
    elif tab_genre == "realestate":
        filtered = [it for it in items if classify(it) == "realestate"]
    elif tab_genre == "bear":
        filtered = [it for it in items if classify(it) == "bear"]
    elif tab_genre == "event":
        filtered = [it for it in items if classify(it) == "event"]
    elif tab_genre == "traffic":
        filtered = [it for it in items if classify(it) == "traffic"]
    elif tab_genre == "sports":
        filtered = [it for it in items if classify(it) == "sports"]
    elif tab_genre == "politics":
        filtered = [it for it in items if classify(it) == "politics"]
    elif tab_genre == "business":
        filtered = [it for it in items if classify(it) == "business"]
    elif tab_genre == "medical":
        filtered = [it for it in items if classify(it) == "medical"]
    elif tab_genre == "weather":
        filtered = [it for it in items if classify(it) == "weather"]
    elif tab_genre == "life":
        filtered = [it for it in items if classify(it) == "life"]
    elif tab_genre == "general":
        filtered = [it for it in items if classify(it) == "general"]
    else:
        filtered = items  # 全件

    if not filtered:
        st.markdown(
            '<div class="empty-state">😔 現在ニュースがありません<br>しばらくしてから更新してください</div>',
            unsafe_allow_html=True,
        )
        return

    for i, item in enumerate(filtered[:100]):
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
        all_items, debug_info = get_news_data()

    if not all_items:
        st.error("ニュースの取得に失敗しました。しばらくしてから更新ボタンを押してください。")
        # デバッグ情報を折りたたんで表示
        with st.expander("🔍 取得状況の詳細（開発者向け）"):
            for src, msg in debug_info.items():
                st.text(f"{src}: {msg}")
        if st.button("🔄 再読み込み"):
            st.cache_data.clear()
            st.rerun()
        return

    # 更新ボタン（ジャンルタブのすぐ上）
    if st.button("🔄 ニュースを更新する", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


    # タブ生成のための件数カウント
    count_crime = sum(1 for it in all_items if classify(it) == "crime")
    count_accident = sum(1 for it in all_items if classify(it) == "accident")
    count_earthquake = sum(1 for it in all_items if classify(it) == "earthquake")
    count_gourmet = sum(1 for it in all_items if classify(it) == "gourmet")
    count_realestate = sum(1 for it in all_items if classify(it) == "realestate")
    count_bear = sum(1 for it in all_items if classify(it) == "bear")
    count_event = sum(1 for it in all_items if classify(it) == "event")
    count_traffic = sum(1 for it in all_items if classify(it) == "traffic")
    count_sports = sum(1 for it in all_items if classify(it) == "sports")
    count_politics = sum(1 for it in all_items if classify(it) == "politics")
    count_business = sum(1 for it in all_items if classify(it) == "business")
    count_medical = sum(1 for it in all_items if classify(it) == "medical")
    count_weather = sum(1 for it in all_items if classify(it) == "weather")
    count_life = sum(1 for it in all_items if classify(it) == "life")
    count_general = sum(1 for it in all_items if classify(it) == "general")

    # タブ
    tab_all, tab_crime, tab_accident, tab_earthquake, tab_gourmet, tab_realestate, tab_bear, tab_event, tab_traffic, tab_sports, tab_politics, tab_business, tab_medical, tab_weather, tab_life, tab_general = st.tabs([
        f"📋 すべて ({len(all_items)})",
        f"🚨 事件 ({count_crime})",
        f"💥 事故 ({count_accident})",
        f"⚠️ 地震 ({count_earthquake})",
        f"🍽️ グルメ ({count_gourmet})",
        f"🏢 不動産 ({count_realestate})",
        f"🐻 熊 ({count_bear})",
        f"🎪 イベント ({count_event})",
        f"🚃 交通 ({count_traffic})",
        f"⚽ スポーツ ({count_sports})",
        f"🏛️ 政治 ({count_politics})",
        f"💼 ビジネス ({count_business})",
        f"🏥 医療 ({count_medical})",
        f"⛅ 天気 ({count_weather})",
        f"🏠 生活 ({count_life})",
        f"📰 その他 ({count_general})",
    ])

    with tab_all:
        render_tab(all_items, tab_genre=None)

    with tab_crime:
        render_tab(all_items, tab_genre="crime")

    with tab_accident:
        render_tab(all_items, tab_genre="accident")

    with tab_earthquake:
        render_tab(all_items, tab_genre="earthquake")

    with tab_gourmet:
        render_tab(all_items, tab_genre="gourmet")

    with tab_realestate:
        render_tab(all_items, tab_genre="realestate")

    with tab_bear:
        render_tab(all_items, tab_genre="bear")

    with tab_event:
        render_tab(all_items, tab_genre="event")

    with tab_traffic:
        render_tab(all_items, tab_genre="traffic")

    with tab_sports:
        render_tab(all_items, tab_genre="sports")

    with tab_politics:
        render_tab(all_items, tab_genre="politics")

    with tab_business:
        render_tab(all_items, tab_genre="business")

    with tab_medical:
        render_tab(all_items, tab_genre="medical")

    with tab_weather:
        render_tab(all_items, tab_genre="weather")

    with tab_life:
        render_tab(all_items, tab_genre="life")

    with tab_general:
        render_tab(all_items, tab_genre="general")

    # デバッグパネル（画面下部に移動）
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("🔍 フィード取得状況", expanded=False):
        for src, msg in debug_info.items():
            st.text(f"{src}: {msg}")


if __name__ == "__main__":
    main()
