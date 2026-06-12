"""
仙台ニュース巡回Webアプリ
Streamlit Cloud 対応・スマホ最適化・電子書籍風ミニマリズムデザイン
"""

import streamlit as st
import json
import os
import datetime
import difflib
import unicodedata

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
@st.cache_data(ttl=900, show_spinner=False)
def get_news_data() -> tuple[list[dict], dict]:
    """無人工場（fetch_news.py）が生成したJSONを読み込む。"""
    try:
        if os.path.exists("news_data.json"):
            with open("news_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("items", []), data.get("debug_info", {})
        else:
            return [], {"system": "news_data.json が見つかりません。"}
    except Exception as e:
        return [], {"system": f"読み込みエラー: {e}"}


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


def clear_search_query(key: str):
    st.session_state[key] = ""

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
        # NFKC正規化で全角・半角（89と８９など）を統一し、最大3単語まで分割してAND検索
        normalized_query = unicodedata.normalize("NFKC", search_query).lower()
        keywords = normalized_query.split()[:3]
        
        filtered = items
        for kw in keywords:
            filtered = [
                it for it in filtered 
                if kw in unicodedata.normalize("NFKC", it.get("title", "")).lower() 
                or kw in unicodedata.normalize("NFKC", it.get("summary", "")).lower()
            ]
        
        # 戻るボタン（コールバックで状態をクリア）
        st.button("⬅️ 前の画面に戻る", key=f"back_{key_suffix}", on_click=clear_search_query, args=(f"search_{key_suffix}",))
            
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
        return

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
