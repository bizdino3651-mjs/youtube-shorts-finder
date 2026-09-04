import streamlit as st
import pandas as pd
import os
import re
from urllib.parse import quote_plus
from datetime import datetime, timezone

# =========================================================
# 🔥 숏파! - Shorts Finder
# 목적:
# 1) 연예인 쇼츠 중복 제거
# 2) 조회수 / 조회수 증가량 / 증가속도 분석
# 3) 쇼핑 관련 키워드 자동 탐지
# 4) 쇼핑 기회 점수 계산
# 5) 오늘의 쇼핑쇼츠 TOP 10 제공
#
# CSV에 아래 컬럼이 있으면 더 정확하게 작동합니다.
# video_id, title, channel_title, view_count, keyword, category,
# timestamp, previous_view_count, previous_checked_at,
# like_count, comment_count
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
.stApp {
    background-color: #f8f9fa;
}
.metric-card {
    background: white;
    border: 1px solid #e9ecef;
    border-radius: 14px;
    padding: 14px;
}
.short-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #e9ecef;
    box-shadow: 0 4px 8px rgba(0,0,0,.04);
    margin-bottom: 18px;
}
.short-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,.08);
}
.short-img {
    width: 100%;
    display: block;
    background: #000;
}
.card-body {
    padding: 14px 16px;
}
.card-title {
    font-size: 14px;
    font-weight: 700;
    line-height: 1.4;
    min-height: 40px;
}
.badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 700;
    margin: 3px 3px 3px 0;
    background: #f1f3f5;
}
.badge-hot {
    background: #fff0f1;
    color: #e03131;
}
.badge-shop {
    background: #fff4d6;
    color: #b26a00;
}
.score {
    font-size: 22px;
    font-weight: 800;
}
.small {
    color: #868e96;
    font-size: 11px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 설정
# -------------------------
DATA_FILE = "shorts_history.csv"

CATEGORY_STRUCTURE = {
    "🔥 인기 아이돌": ["장원영", "카리나", "안유진", "윈터", "아이브", "에스파"],
    "💄 패션/뷰티 인플루언서": ["프리지아", "이사배", "뷰티", "메이크업", "화장"],
    "⭐ 셀럽 / 라이프스타일": ["김나영", "강민경", "셀럽", "연예인"],
    "🛍️ 쇼핑 인텐트": [
        "공항패션", "내돈내산", "왓츠인마이백", "애착템",
        "최애템", "추천템", "구매템", "쇼핑", "사용템"
    ]
}

SHOPPING_TERMS = {
    "화장품": [
        "립", "립스틱", "틴트", "쿠션", "파운데이션", "선크림",
        "크림", "에센스", "세럼", "앰플", "토너", "마스크팩",
        "향수", "샴푸", "트리트먼트", "화장품", "메이크업"
    ],
    "패션": [
        "가방", "백", "신발", "운동화", "구두", "자켓", "재킷",
        "코트", "패딩", "니트", "셔츠", "원피스", "바지", "팬츠",
        "스커트", "청바지", "모자", "안경", "선글라스", "시계"
    ],
    "생활": [
        "텀블러", "주방", "냄비", "후라이팬", "수세미", "청소",
        "정리", "수납", "빗자루", "거름망", "선반", "용품",
        "생활용품", "가전", "전자레인지"
    ],
    "식품": [
        "커피", "차", "간식", "과자", "라면", "음료", "식품",
        "디저트", "빵", "떡", "소스"
    ],
    "디지털": [
        "아이폰", "갤럭시", "이어폰", "에어팟", "키보드", "마우스",
        "충전기", "스피커", "카메라", "노트북", "태블릿"
    ],
    "육아/반려": [
        "아기", "유아", "장난감", "강아지", "고양이", "반려동물"
    ]
}

SHOPPING_INTENT_TERMS = [
    "내돈내산", "추천", "추천템", "애착템", "최애템", "구매",
    "샀", "산", "사용", "사용템", "왓츠인마이백", "가방",
    "공항패션", "착용", "착장", "제품", "아이템", "정보",
    "어디꺼", "어디 것", "브랜드", "쇼핑"
]

# -------------------------
# 데이터 로드
# -------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        data = pd.read_csv(DATA_FILE)
    else:
        data = pd.DataFrame([
            {
                "video_id": "demo001",
                "title": "[김나영] 내돈내산 최애템 추천",
                "channel_title": "Demo Channel",
                "view_count": 1800000,
                "previous_view_count": 1200000,
                "keyword": "김나영",
                "category": "⭐ 셀럽 / 라이프스타일",
                "timestamp": "2026-09-04 10:00:00",
                "previous_checked_at": "2026-09-04 04:00:00",
                "like_count": 85000,
                "comment_count": 3200
            },
            {
                "video_id": "demo002",
                "title": "[장원영] 공항패션 가방 어디꺼?",
                "channel_title": "Fashion Demo",
                "view_count": 950000,
                "previous_view_count": 650000,
                "keyword": "장원영",
                "category": "🔥 인기 아이돌",
                "timestamp": "2026-09-04 08:00:00",
                "previous_checked_at": "2026-09-04 02:00:00",
                "like_count": 42000,
                "comment_count": 1800
            },
            {
                "video_id": "demo003",
                "title": "[카리나] 요즘 쓰는 향수 공개",
                "channel_title": "Beauty Demo",
                "view_count": 720000,
                "previous_view_count": 500000,
                "keyword": "카리나",
                "category": "🔥 인기 아이돌",
                "timestamp": "2026-09-04 12:00:00",
                "previous_checked_at": "2026-09-04 06:00:00",
                "like_count": 31000,
                "comment_count": 1200
            }
        ])
    return data


df = load_data()

# -------------------------
# 필수 컬럼 보정
# -------------------------
required_defaults = {
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

for col, default in required_defaults.items():
    if col not in df.columns:
        df[col] = default

# 숫자형 정리
for col in ["view_count", "previous_view_count", "like_count", "comment_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["previous_checked_at"] = pd.to_datetime(
    df["previous_checked_at"], errors="coerce"
)

# =========================================================
# ① 중복 제거
# 같은 video_id는 무조건 한 건만 표시
# =========================================================
df = df.drop_duplicates(subset=["video_id"], keep="first").copy()

# =========================================================
# ② 조회수 증가량 / 증가속도
# previous_view_count가 없거나 0이면 성장률은 계산하지 않음
# =========================================================
df["view_growth"] = (
    df["view_count"] - df["previous_view_count"]
).clip(lower=0)

df["check_hours"] = (
    (df["timestamp"] - df["previous_checked_at"])
    .dt.total_seconds()
    .div(3600)
)

df["check_hours"] = df["check_hours"].where(
    df["check_hours"] > 0
)

df["view_growth_per_hour"] = (
    df["view_growth"] / df["check_hours"]
).fillna(0)

# 업로드 후 경과시간
now = pd.Timestamp.now(tz=None)
df["age_hours"] = (
    (now - df["timestamp"]).dt.total_seconds() / 3600
).clip(lower=0.25)

df["avg_views_per_hour"] = (
    df["view_count"] / df["age_hours"]
).fillna(0)

# =========================================================
# ③ 쇼핑 키워드 자동 탐지
# =========================================================
def detect_products(row):
    text = f"{row.get('title', '')} {row.get('keyword', '')}".lower()

    found_categories = []
    found_terms = []

    for category, terms in SHOPPING_TERMS.items():
        matched = [term for term in terms if term.lower() in text]
        if matched:
            found_categories.append(category)
            found_terms.extend(matched)

    return found_categories, found_terms


detected = df.apply(detect_products, axis=1)
df["product_categories"] = detected.apply(lambda x: ", ".join(x[0]))
df["product_keywords"] = detected.apply(
    lambda x: ", ".join(dict.fromkeys(x[1]))
)

# 쇼핑 인텐트
df["shopping_intent_count"] = df.apply(
    lambda row: sum(
        1 for term in SHOPPING_INTENT_TERMS
        if term.lower() in (
            f"{row['title']} {row['keyword']}"
        ).lower()
    ),
    axis=1
)

# =========================================================
# ④ 쇼핑 기회 점수
# 조회수 + 증가속도 + 쇼핑의도 + 참여도
# 100점 기준
# =========================================================
def normalize(series):
    if len(series) == 0:
        return series
    max_v = series.max()
    if max_v <= 0:
        return pd.Series(0, index=series.index)
    return (series / max_v * 100).clip(0, 100)


view_score = normalize(df["view_count"])
growth_score = normalize(df["view_growth_per_hour"])

engagement_rate = (
    (df["like_count"] + df["comment_count"]) /
    df["view_count"].replace(0, 1)
)
engagement_score = normalize(engagement_rate)

intent_score = (
    df["shopping_intent_count"].clip(0, 5) / 5 * 100
)

product_score = (
    df["product_keywords"].str.len().gt(0).astype(int) * 100
)

df["shopping_score"] = (
    view_score * 0.25 +
    growth_score * 0.35 +
    intent_score * 0.20 +
    product_score * 0.15 +
    engagement_score * 0.05
).round(0).astype(int)

# =========================================================
# ⑤ 등급
# =========================================================
def score_grade(score):
    if score >= 90:
        return "🔥🔥🔥 S급"
    if score >= 80:
        return "🔥🔥 A급"
    if score >= 70:
        return "🔥 B급"
    if score >= 60:
        return "👀 관찰"
    return "일반"


df["grade"] = df["shopping_score"].apply(score_grade)

# 썸네일
df["thumbnail_url"] = df["video_id"].apply(
    lambda x: f"https://img.youtube.com/vi/{x}/hqdefault.jpg"
)

# =========================================================
# 화면
# =========================================================
st.title("🔥 숏파! - Shorts Finder 🔥")
st.caption("Find What's Trending. 뜨는 쇼츠를 찾아드립니다.")

# 상단 메트릭
c1, c2, c3, c4 = st.columns(4)

c1.metric("총 수집 쇼츠", f"{len(df):,}개")
c2.metric("수집 키워드", f"{df['keyword'].nunique():,}개")

top_view = df["view_count"].max() if not df.empty else 0
c3.metric(
    "최고 조회수",
    f"{top_view / 10000:.1f}만회" if top_view >= 10000 else f"{int(top_view):,}회"
)

latest = df["timestamp"].max()
c4.metric(
    "최근 업데이트",
    latest.strftime("%m/%d %H:%M") if pd.notna(latest) else "-"
)

st.divider()

# =========================================================
# 오늘의 쇼핑 기회 TOP 10
# =========================================================
st.subheader("🚨 오늘의 쇼핑쇼츠 TOP 10")

top10 = df.sort_values(
    ["shopping_score", "view_growth_per_hour", "view_count"],
    ascending=False
).head(10)

if not top10.empty:
    top_cols = st.columns(min(5, len(top10)))

    for rank, (_, item) in enumerate(top10.iterrows(), start=1):
        with top_cols[(rank - 1) % len(top_cols)]:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div><b>#{rank} {item['grade']}</b></div>
                    <div class="score">{item['shopping_score']}점</div>
                    <div class="small">쇼핑 기회 점수</div>
                    <hr>
                    <b>{item['keyword']}</b><br>
                    👀 {int(item['view_count']):,}회<br>
                    🚀 +{int(item['view_growth']):,}회<br>
                    ⚡ 시간당 +{int(item['view_growth_per_hour']):,}회
                </div>
                """,
                unsafe_allow_html=True
            )

st.divider()

# =========================================================
# 검색 / 필터
# =========================================================
st.subheader("🔍 연예인 쇼핑 키워드 탐색")

f1, f2, f3 = st.columns([1, 1, 1])

with f1:
    selected_cat = st.selectbox(
        "1차 카테고리",
        ["전체"] + list(CATEGORY_STRUCTURE.keys())
    )

with f2:
    if selected_cat == "전체":
        sub_options = ["전체"] + list(dict.fromkeys(
            item
            for items in CATEGORY_STRUCTURE.values()
            for item in items
        ))
    else:
        sub_options = ["전체"] + CATEGORY_STRUCTURE[selected_cat]

    selected_sub = st.selectbox(
        "2차 세부 인물/테마",
        sub_options
    )

with f3:
    search_query = st.text_input(
        "제목 / 채널명 / 인물명 통합 검색"
    )

# 빠른 검색
st.write("📌 **빠른 트렌드**")

quick_chips = [
    "전체", "장원영", "카리나", "프리지아",
    "김나영", "공항패션", "내돈내산", "애착템"
]

chip_cols = st.columns(len(quick_chips))

if "selected_chip" not in st.session_state:
    st.session_state.selected_chip = "전체"

for i, chip in enumerate(quick_chips):
    with chip_cols[i]:
        if st.button(
            chip if chip != "전체" else "🔄 전체",
            key=f"chip_{i}",
            use_container_width=True
        ):
            st.session_state.selected_chip = chip

if st.session_state.selected_chip != "전체":
    st.caption(
        f"현재 빠른 필터: **#{st.session_state.selected_chip}**"
    )

# =========================================================
# 필터 적용
# =========================================================
filtered = df.copy()

def row_search_text(frame):
    return (
        frame["title"].fillna("").astype(str) + " " +
        frame["keyword"].fillna("").astype(str) + " " +
        frame["channel_title"].fillna("").astype(str) + " " +
        frame["product_keywords"].fillna("").astype(str)
    )

search_text = row_search_text(filtered)

if selected_sub != "전체":
    filtered = filtered[
        search_text.str.contains(
            re.escape(selected_sub),
            case=False,
            na=False
        )
    ]

elif selected_cat != "전체":
    keywords = CATEGORY_STRUCTURE[selected_cat]
    pattern = "|".join(re.escape(x) for x in keywords)

    filtered = filtered[
        search_text.str.contains(
            pattern,
            case=False,
            na=False
        )
    ]

if st.session_state.selected_chip != "전체":
    chip = st.session_state.selected_chip
    chip_text = row_search_text(filtered)

    filtered = filtered[
        chip_text.str.contains(
            re.escape(chip),
            case=False,
            na=False
        )
    ]

if search_query.strip():
    search_text = row_search_text(filtered)

    filtered = filtered[
        search_text.str.contains(
            re.escape(search_query.strip()),
            case=False,
            na=False
        )
    ]

# =========================================================
# 정렬 방식
# =========================================================
st.divider()
st.subheader(f"🔥 검색 결과 ({len(filtered):,}건)")

sort_option = st.selectbox(
    "정렬 기준",
    [
        "쇼핑 기회 점수순",
        "조회수 증가속도순",
        "조회수 증가량순",
        "조회수순",
        "최신 업로드순"
    ]
)

if sort_option == "쇼핑 기회 점수순":
    result_df = filtered.sort_values(
        ["shopping_score", "view_growth_per_hour"],
        ascending=False
    )
elif sort_option == "조회수 증가속도순":
    result_df = filtered.sort_values(
        "view_growth_per_hour",
        ascending=False
    )
elif sort_option == "조회수 증가량순":
    result_df = filtered.sort_values(
        "view_growth",
        ascending=False
    )
elif sort_option == "최신 업로드순":
    result_df = filtered.sort_values(
        "timestamp",
        ascending=False
    )
else:
    result_df = filtered.sort_values(
        "view_count",
        ascending=False
    )

# =========================================================
# 카드
# =========================================================
if result_df.empty:
    st.warning("조건에 맞는 쇼츠가 없습니다.")
else:
    cols_per_row = 4

    for start in range(0, len(result_df), cols_per_row):
        row = result_df.iloc[start:start + cols_per_row]
        cols = st.columns(cols_per_row)

        for idx, (_, item) in enumerate(row.iterrows()):
            with cols[idx]:
                video_url = (
                    f"https://www.youtube.com/shorts/{item['video_id']}"
                )

                views = int(item["view_count"])
                growth = int(item["view_growth"])
                velocity = int(item["view_growth_per_hour"])

                if views >= 100000000:
                    views_text = f"{views / 100000000:.2f}억"
                elif views >= 10000:
                    views_text = f"{views / 10000:.1f}만"
                else:
                    views_text = f"{views:,}"

                if velocity >= 10000:
                    velocity_text = f"{velocity / 10000:.1f}만/시간"
                else:
                    velocity_text = f"{velocity:,}/시간"

                product_text = (
                    item["product_keywords"]
                    if item["product_keywords"]
                    else "상품 키워드 미탐지"
                )

                shopping_search = quote_plus(
                    f"{item['keyword']} {product_text.split(',')[0]}"
                )

                st.markdown(
                    f"""
                    <a href="{video_url}" target="_blank"
                       style="text-decoration:none;color:inherit;">
                        <div class="short-card">
                            <img src="{item['thumbnail_url']}"
                                 class="short-img">
                            <div class="card-body">
                                <div class="card-title">
                                    {item['title']}
                                </div>

                                <div style="margin-top:8px;">
                                    <span class="badge badge-hot">
                                        {item['grade']}
                                    </span>
                                    <span class="badge">
                                        점수 {item['shopping_score']}
                                    </span>
                                    <span class="badge">
                                        👀 {views_text}
                                    </span>
                                </div>

                                <div style="margin-top:7px;">
                                    🚀 +{growth:,}회<br>
                                    ⚡ {velocity_text}
                                </div>

                                <div style="margin-top:8px;">
                                    <span class="badge badge-shop">
                                        🛒 {product_text}
                                    </span>
                                </div>

                                <div class="small" style="margin-top:7px;">
                                    @{item['channel_title']}
                                </div>
                            </div>
                        </div>
                    </a>
                    """,
                    unsafe_allow_html=True
                )

                st.link_button(
                    "🛒 상품 검색어 확인",
                    f"https://www.google.com/search?q={shopping_search}",
                    use_container_width=True
                )

# =========================================================
# 데이터 상태 안내
# =========================================================
st.divider()
with st.expander("ℹ️ 조회수 증가속도는 어떻게 계산되나요?"):
    st.write(
        """
        Short Finder가 진짜 '급상승'을 잡으려면 같은 영상을 여러 번 수집해서
        이전 조회수와 현재 조회수를 비교해야 합니다.

        필요한 핵심 컬럼:
        - previous_view_count : 직전 수집 당시 조회수
        - previous_checked_at : 직전 수집 시간
        - view_count : 현재 조회수
        - timestamp : 현재 수집 시간

        계산:
        조회수 증가량 = 현재 조회수 - 이전 조회수

        시간당 증가속도 =
        조회수 증가량 ÷ 두 번의 수집 사이 경과시간
        """
    )

st.caption(
    "🔥 Find What's Trending. 뜨는 쇼츠를 찾아드립니다."
)
