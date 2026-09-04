import streamlit as st
import pandas as pd
import os
import re
import html
import requests
from urllib.parse import quote_plus

# =========================================================
# 🔥 숏파! - Shorts Finder V3
# 핵심:
# 1. 기존 저장 데이터 탐색
# 2. YouTube 실시간 자유 검색
# 3. "연예인 + 아이템" 형태 검색
# 4. 조회수/좋아요/댓글/업로드일 표시
# 5. 쇼핑 인텐트 + 쇼핑 기회 점수
#
# Streamlit Secrets:
# [youtube]
# api_key = "AIzaSyByLxL2oMJ6j6gqtESk8mou98TktqavwJw"
#
# 또는
# YOUTUBE_API_KEY = "AIzaSyByLxL2oMJ6j6gqtESk8mou98TktqavwJw"
# =========================================================

st.set_page_config(
    page_title="🔥 숏파! - Shorts Finder",
    layout="wide",
    page_icon="🔥"
)

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>
.stApp { background:#f8f9fa; }
.short-card {
    background:#fff;
    border:1px solid #e9ecef;
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 4px 10px rgba(0,0,0,.05);
    margin-bottom:12px;
}
.short-card:hover {
    transform:translateY(-2px);
    box-shadow:0 10px 20px rgba(0,0,0,.09);
}
.short-img {
    width:100%;
    aspect-ratio:9/16;
    object-fit:cover;
    display:block;
    background:#000;
}
.card-body { padding:12px 14px 14px; }
.card-title {
    font-size:14px;
    font-weight:700;
    line-height:1.45;
    min-height:42px;
}
.badge {
    display:inline-block;
    padding:4px 7px;
    border-radius:7px;
    font-size:10px;
    font-weight:700;
    margin:3px 2px 2px 0;
    background:#f1f3f5;
}
.badge-hot { background:#fff0f1; color:#e03131; }
.badge-shop { background:#fff4d6; color:#a85d00; }
.small { color:#868e96; font-size:11px; }
.score {
    font-size:20px;
    font-weight:800;
}
.search-box {
    background:#fff;
    border:1px solid #e9ecef;
    border-radius:16px;
    padding:18px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 설정
# -------------------------
DATA_FILE = "shorts_history.csv"

CATEGORY_STRUCTURE = {
    "🔥 인기 아이돌": ["장원영", "카리나", "안유진", "윈터", "아이브", "에스파"],
    "💄 패션/뷰티 인플루언서": ["프리지아", "이사배", "뷰티", "메이크업"],
    "⭐ 셀럽 / 라이프스타일": ["김나영", "강민경", "셀럽", "연예인"],
    "🛍️ 쇼핑 인텐트": [
        "공항패션", "내돈내산", "왓츠인마이백",
        "애착템", "최애템", "추천템", "구매템", "쇼핑"
    ]
}

SHOPPING_TERMS = {
    "화장품": [
        "립", "립스틱", "틴트", "쿠션", "파운데이션", "선크림",
        "크림", "에센스", "세럼", "앰플", "토너", "향수",
        "샴푸", "트리트먼트", "화장품", "메이크업"
    ],
    "패션": [
        "가방", "백", "신발", "운동화", "구두", "자켓", "재킷",
        "코트", "패딩", "니트", "셔츠", "원피스", "바지",
        "팬츠", "스커트", "청바지", "모자", "안경", "선글라스", "시계"
    ],
    "생활": [
        "텀블러", "주방", "냄비", "후라이팬", "수세미", "청소",
        "정리", "수납", "빗자루", "거름망", "선반", "생활용품",
        "가전", "용품"
    ],
    "디지털": [
        "아이폰", "갤럭시", "이어폰", "에어팟", "키보드", "마우스",
        "충전기", "스피커", "카메라", "노트북", "태블릿"
    ],
    "식품": [
        "커피", "차", "간식", "과자", "음료", "식품", "디저트", "빵"
    ]
}

SHOPPING_INTENT_TERMS = [
    "내돈내산", "추천", "추천템", "애착템", "최애템",
    "구매", "샀", "사용", "사용템", "왓츠인마이백",
    "공항패션", "착용", "착장", "제품", "아이템",
    "정보", "어디꺼", "어디 것", "브랜드", "쇼핑"
]

# -------------------------
# API Key
# -------------------------
def get_api_key():
    try:
        if "youtube" in st.secrets and "api_key" in st.secrets["youtube"]:
            return st.secrets["youtube"]["api_key"]
    except Exception:
        pass

    try:
        if "YOUTUBE_API_KEY" in st.secrets:
            return st.secrets["YOUTUBE_API_KEY"]
    except Exception:
        pass

    return os.getenv("YOUTUBE_API_KEY", "").strip()


# -------------------------
# 공통 함수
# -------------------------
def format_views(n):
    n = int(n or 0)
    if n >= 100000000:
        return f"{n / 100000000:.2f}억"
    if n >= 10000:
        return f"{n / 10000:.1f}만"
    return f"{n:,}"


def detect_products(title, keyword=""):
    text = f"{title} {keyword}".lower()
    categories = []
    terms = []

    for category, words in SHOPPING_TERMS.items():
        matched = [w for w in words if w.lower() in text]
        if matched:
            categories.append(category)
            terms.extend(matched)

    return categories, list(dict.fromkeys(terms))


def calculate_shopping_score(row):
    title = str(row.get("title", ""))
    keyword = str(row.get("keyword", ""))
    text = f"{title} {keyword}".lower()

    intent = sum(
        1 for term in SHOPPING_INTENT_TERMS
        if term.lower() in text
    )

    _, product_terms = detect_products(title, keyword)

    views = float(row.get("view_count", 0) or 0)
    likes = float(row.get("like_count", 0) or 0)
    comments = float(row.get("comment_count", 0) or 0)

    # 실시간 검색은 증가속도 데이터가 없으므로
    # 조회수 + 쇼핑의도 + 상품키워드 + 참여도로 점수화
    view_score = min(100, (views / 1000000) * 25)
    intent_score = min(30, intent * 6)
    product_score = min(25, len(product_terms) * 8)

    engagement = (
        (likes + comments) / max(views, 1)
    )
    engagement_score = min(20, engagement * 1000)

    score = round(
        view_score +
        intent_score +
        product_score +
        engagement_score
    )

    return min(100, score)


def load_saved_data():
    if os.path.exists(DATA_FILE):
        data = pd.read_csv(DATA_FILE)
    else:
        data = pd.DataFrame(columns=[
            "video_id", "title", "channel_title", "view_count",
            "keyword", "category", "timestamp",
            "previous_view_count", "previous_checked_at",
            "like_count", "comment_count"
        ])

    defaults = {
        "video_id": "",
        "title": "",
        "channel_title": "",
        "view_count": 0,
        "keyword": "",
        "category": "",
        "timestamp": "",
        "previous_view_count": 0,
        "previous_checked_at": "",
        "like_count": 0,
        "comment_count": 0
    }

    for col, default in defaults.items():
        if col not in data.columns:
            data[col] = default

    for col in ["view_count", "previous_view_count", "like_count", "comment_count"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    data = data.drop_duplicates("video_id", keep="first")
    return data


def youtube_search(query, order="relevance", max_results=24):
    api_key = get_api_key()

    if not api_key:
        st.error(
            "YouTube API 키를 찾지 못했습니다. "
            "Streamlit Secrets에 [youtube] api_key를 등록해주세요."
        )
        return pd.DataFrame()

    search_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": order,
        "regionCode": "KR",
        "relevanceLanguage": "ko",
        "safeSearch": "moderate",
        "videoDuration": "short",
        "key": api_key
    }

    try:
        response = requests.get(
            search_url,
            params=params,
            timeout=20
        )

        if response.status_code != 200:
            try:
                message = response.json()["error"]["message"]
            except Exception:
                message = response.text[:300]

            st.error(f"YouTube API 오류: {message}")
            return pd.DataFrame()

        items = response.json().get("items", [])

        video_ids = [
            item["id"]["videoId"]
            for item in items
            if item.get("id", {}).get("videoId")
        ]

        if not video_ids:
            return pd.DataFrame()

        # 검색 결과의 통계/길이를 videos.list로 보강
        stats_url = "https://www.googleapis.com/youtube/v3/videos"

        stats_response = requests.get(
            stats_url,
            params={
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(video_ids),
                "key": api_key
            },
            timeout=20
        )

        if stats_response.status_code != 200:
            try:
                message = stats_response.json()["error"]["message"]
            except Exception:
                message = stats_response.text[:300]
            st.error(f"YouTube 영상 정보 오류: {message}")
            return pd.DataFrame()

        stats_items = stats_response.json().get("items", [])

        stats_map = {
            item["id"]: item
            for item in stats_items
        }

        rows = []

        for item in items:
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue

            snippet = item.get("snippet", {})
            detail = stats_map.get(video_id, {})
            statistics = detail.get("statistics", {})
            content = detail.get("contentDetails", {})

            title = snippet.get("title", "")
            channel = snippet.get("channelTitle", "")
            published = snippet.get("publishedAt", "")

            _, product_terms = detect_products(title, query)

            row = {
                "video_id": video_id,
                "title": title,
                "channel_title": channel,
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "keyword": query,
                "category": "🔎 실시간 검색",
                "timestamp": published,
                "duration": content.get("duration", ""),
                "product_keywords": ", ".join(product_terms),
            }

            rows.append(row)

        result = pd.DataFrame(rows)

        if result.empty:
            return result

        result["shopping_score"] = result.apply(
            calculate_shopping_score,
            axis=1
        )

        result["grade"] = result["shopping_score"].apply(
            lambda x:
                "🔥🔥🔥 S급" if x >= 90 else
                "🔥🔥 A급" if x >= 80 else
                "🔥 B급" if x >= 70 else
                "👀 관찰" if x >= 60 else
                "일반"
        )

        result["thumbnail_url"] = result["video_id"].apply(
            lambda x:
                f"https://img.youtube.com/vi/{x}/hqdefault.jpg"
        )

        return result

    except requests.RequestException as e:
        st.error(f"인터넷 연결 오류: {e}")
        return pd.DataFrame()


# =========================================================
# 화면 시작
# =========================================================
st.title("🔥 숏파! - Shorts Finder 🔥")
st.caption("Find What's Trending. 뜨는 쇼츠를 찾아드립니다.")

saved_df = load_saved_data()

# =========================================================
# ⭐ 핵심: YouTube 자유 검색
# =========================================================
st.markdown("### 🔎 YouTube 쇼츠 자유 검색")

st.markdown('<div class="search-box">', unsafe_allow_html=True)

search_col, order_col, button_col = st.columns([5, 1.5, 1.2])

with search_col:
    live_query = st.text_input(
        "검색어",
        placeholder="예: 제니 가방 / 김혜수 향수 / 아이유 옷 / 차은우 시계",
        label_visibility="collapsed"
    )

with order_col:
    live_order = st.selectbox(
        "정렬",
        ["relevance", "viewCount", "date"],
        format_func=lambda x: {
            "relevance": "관련성",
            "viewCount": "조회수",
            "date": "최신"
        }[x],
        label_visibility="collapsed"
    )

with button_col:
    search_clicked = st.button(
        "🔍 검색",
        type="primary",
        use_container_width=True
    )

st.caption(
    "💡 연예인 이름만 입력해도 되고, **연예인 + 상품명**으로 검색하면 쇼핑 소재를 찾기 쉽습니다."
)

st.markdown("</div>", unsafe_allow_html=True)

# 검색 실행
if search_clicked:
    if not live_query.strip():
        st.warning("검색어를 입력해주세요.")
    else:
        with st.spinner(f"'{live_query}' YouTube 검색 중..."):
            st.session_state["live_results"] = youtube_search(
                live_query.strip(),
                order=live_order,
                max_results=24
            )
            st.session_state["live_query"] = live_query.strip()

# 검색 결과
if "live_results" in st.session_state:
    live_df = st.session_state["live_results"]

    if not live_df.empty:
        st.divider()

        q = st.session_state.get("live_query", "")
        st.subheader(
            f"🔥 '{q}' 검색 결과 ({len(live_df)}건)"
        )

        sort_mode = st.selectbox(
            "검색 결과 정렬",
            [
                "쇼핑 기회 점수순",
                "조회수순",
                "좋아요순",
                "댓글순",
                "최신순"
            ],
            key="live_sort"
        )

        if sort_mode == "쇼핑 기회 점수순":
            display_df = live_df.sort_values(
                "shopping_score", ascending=False
            )
        elif sort_mode == "조회수순":
            display_df = live_df.sort_values(
                "view_count", ascending=False
            )
        elif sort_mode == "좋아요순":
            display_df = live_df.sort_values(
                "like_count", ascending=False
            )
        elif sort_mode == "댓글순":
            display_df = live_df.sort_values(
                "comment_count", ascending=False
            )
        else:
            display_df = live_df.sort_values(
                "timestamp", ascending=False
            )

        cols_per_row = 4

        for start in range(0, len(display_df), cols_per_row):
            row = display_df.iloc[start:start + cols_per_row]
            cols = st.columns(cols_per_row)

            for idx, (_, item) in enumerate(row.iterrows()):
                with cols[idx]:
                    video_url = (
                        f"https://www.youtube.com/shorts/{item['video_id']}"
                    )

                    title = html.escape(str(item["title"]))
                    channel = html.escape(
                        str(item["channel_title"])
                    )
                    products = html.escape(
                        str(item.get("product_keywords", ""))
                    )

                    if not products:
                        products = "상품 키워드 미탐지"

                    card_html = (
                        f'<a href="{video_url}" target="_blank" '
                        f'style="text-decoration:none;color:inherit;">'
                        f'<div class="short-card">'
                        f'<img src="{item["thumbnail_url"]}" '
                        f'class="short-img">'
                        f'<div class="card-body">'
                        f'<div class="card-title">{title}</div>'
                        f'<span class="badge badge-hot">'
                        f'{item["grade"]}</span>'
                        f'<span class="badge">'
                        f'점수 {item["shopping_score"]}</span>'
                        f'<span class="badge">'
                        f'👀 {format_views(item["view_count"])}</span>'
                        f'<div style="margin-top:7px;">'
                        f'❤️ {format_views(item["like_count"])} '
                        f'💬 {format_views(item["comment_count"])}'
                        f'</div>'
                        f'<div style="margin-top:8px;">'
                        f'<span class="badge badge-shop">'
                        f'🛒 {products}</span>'
                        f'</div>'
                        f'<div class="small" style="margin-top:7px;">'
                        f'@{channel}</div>'
                        f'</div></div></a>'
                    )

                    st.markdown(
                        card_html,
                        unsafe_allow_html=True
                    )

                    st.link_button(
                        "▶️ YouTube에서 보기",
                        video_url,
                        use_container_width=True
                    )

    else:
        st.info("검색 결과가 없습니다.")

# =========================================================
# 기존 저장 데이터
# =========================================================
st.divider()
st.subheader("📚 저장된 트렌드 데이터")

if saved_df.empty:
    st.info(
        "저장된 데이터가 없습니다. "
        "YouTube 자유 검색을 사용해보세요."
    )
else:
    saved_df["thumbnail_url"] = saved_df["video_id"].apply(
        lambda x:
            f"https://img.youtube.com/vi/{x}/hqdefault.jpg"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("총 수집 쇼츠", f"{len(saved_df):,}개")
    c2.metric("수집 키워드", f"{saved_df['keyword'].nunique():,}개")
    c3.metric(
        "최고 조회수",
        format_views(saved_df["view_count"].max())
    )

    f1, f2 = st.columns([1, 2])

    with f1:
        selected_cat = st.selectbox(
            "카테고리",
            ["전체"] + list(CATEGORY_STRUCTURE.keys()),
            key="saved_cat"
        )

    with f2:
        saved_search = st.text_input(
            "저장 데이터 검색",
            placeholder="장원영, 카리나, 가방, 내돈내산..."
        )

    filtered = saved_df.copy()

    if selected_cat != "전체":
        keywords = CATEGORY_STRUCTURE[selected_cat]
        pattern = "|".join(re.escape(x) for x in keywords)

        text = (
            filtered["title"].fillna("").astype(str) + " " +
            filtered["keyword"].fillna("").astype(str) + " " +
            filtered["channel_title"].fillna("").astype(str)
        )

        filtered = filtered[
            text.str.contains(
                pattern,
                case=False,
                na=False
            )
        ]

    if saved_search.strip():
        text = (
            filtered["title"].fillna("").astype(str) + " " +
            filtered["keyword"].fillna("").astype(str) + " " +
            filtered["channel_title"].fillna("").astype(str)
        )

        filtered = filtered[
            text.str.contains(
                re.escape(saved_search.strip()),
                case=False,
                na=False
            )
        ]

    filtered = filtered.sort_values(
        "view_count",
        ascending=False
    )

    st.caption(f"현재 저장 데이터 검색 결과: {len(filtered):,}건")

# =========================================================
# API 안내
# =========================================================
with st.expander("⚙️ YouTube API 설정 방법"):
    st.markdown("""
**Streamlit Secrets에 아래처럼 넣어주세요.**

```toml
[youtube]
api_key = "여기에_YouTube_API_키"
```

기존 API 키를 그대로 사용할 수 있습니다.

이 버전의 실시간 검색은 YouTube Data API의 `search.list`로 영상을 검색하고,
`videos.list`로 조회수·좋아요·댓글 등의 통계를 보강합니다.
""")

st.caption(
    "🔥 Find What's Trending. 뜨는 쇼츠를 찾아드립니다."
)
