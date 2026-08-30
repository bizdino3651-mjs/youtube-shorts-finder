import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="숏파! - Shorts Finder",
    layout="wide",
    page_icon="🔥"
)

# --- 트렌디한 모던 카드 UI 스타일링 ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .shorts-card {
        background-color: #ffffff;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.25s ease;
        margin-bottom: 20px;
    }
    .shorts-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.1);
        border-color: #dee2e6;
    }
    .img-container { width: 100%; position: relative; background-color: #000; overflow: hidden; }
    .shorts-img { width: 100%; height: auto; display: block; object-fit: contain; }
    .card-content { padding: 14px 16px; }
    .card-title {
        font-size: 14px; font-weight: 700; color: #212529; line-height: 1.4;
        height: 40px; display: -webkit-box; -webkit-line-clamp: 2;
        -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 10px;
    }
    .card-info { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #6c757d; }
    .view-badge { background-color: #fff0f1; color: #ff0033; font-weight: 700; padding: 4px 8px; border-radius: 6px; font-size: 11px; }
    .channel-name { font-weight: 500; max-width: 110px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    </style>
""", unsafe_allow_html=True)

# 1. 메인 타이틀
st.title("🔥 숏파! - Shorts Finder 🔥")

# 세션 상태 초기화 (칩 선택 상태 관리)
if "selected_chip" not in st.session_state:
    st.session_state.selected_chip = None

CATEGORY_STRUCTURE = {
    "🔥 인기 아이돌": ["장원영", "카리나", "안유진", "윈터"],
    "💄 패션/뷰티 인플루언서": ["프리지아", "이사배"],
    "⭐ 셀럽 / 라이프스타일": ["김나영", "강민경"],
    "🛍️ 쇼핑 인텐트 (공통)": ["공항패션", "내돈내산", "왓츠인마이백", "애착템"]
}

# 데이터 로드
filename = "shorts_history.csv"
if os.path.exists(filename):
    df = pd.read_csv(filename)
else:
    dummy_data = [
        {"video_id": "3oA81c3yW48", "title": "[아이돌] 장원영 미우미우 가방 착장 정보 👜", "channel_title": "아이돌스케치", "view_count": 1200000, "keyword": "장원영", "category": "🔥 인기 아이돌", "timestamp": "2026-08-30 10:00:00"},
        {"video_id": "6ZUIwj3YeUY", "title": "[아이돌] 카리나 성수동 팝업스토어 착장 모음 🔥", "channel_title": "OOTD모음", "view_count": 850000, "keyword": "카리나", "category": "🔥 인기 아이돌", "timestamp": "2026-08-30 11:00:00"},
        {"video_id": "5v2U9U9U1Rk", "title": "[아이돌] 안유진 공항패션 자켓 어디꺼?", "channel_title": "패션인사이드", "view_count": 640000, "keyword": "안유진", "category": "🔥 인기 아이돌", "timestamp": "2026-08-30 09:30:00"},
        {"video_id": "3oA81c3yW48", "title": "[인플루언서] 프리지아 최애 향수 & 파우치공개 💄", "channel_title": "뷰티파우치", "view_count": 920000, "keyword": "프리지아", "category": "💄 패션/뷰티 인플루언서", "timestamp": "2026-08-30 08:10:00"},
        {"video_id": "6ZUIwj3YeUY", "title": "[셀럽] 김나영 노필터선물 내돈내산 패션 🛍️", "channel_title": "라이프스타일", "view_count": 510000, "keyword": "김나영", "category": "⭐ 셀럽 / 라이프스타일", "timestamp": "2026-08-30 07:40:00"},
        {"video_id": "5v2U9U9U1Rk", "title": "[테마] 연예인 내돈내산 애착템 추천 🌟", "channel_title": "트렌드픽", "view_count": 1800000, "keyword": "내돈내산", "category": "🛍️ 쇼핑 인텐트 (공통)", "timestamp": "2026-08-30 06:10:00"}
    ]
    df = pd.DataFrame(dummy_data)

if not df.empty:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['thumbnail_url'] = df['video_id'].apply(lambda x: f"https://img.youtube.com/vi/{x}/hqdefault.jpg")

    # 상단 요약 통계
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 수집 쇼츠", f"{len(df)}개")
    col2.metric("수집 키워드", f"{df['keyword'].nunique()}개")
    top_view = df.sort_values(by="view_count", ascending=False).iloc[0]
    col3.metric("최고 조회수", f"{top_view['view_count']/10000:.1f}만회")
    col4.metric("최근 업데이트", df['timestamp'].max().strftime('%m/%d %H:%M'))

    st.divider()

    st.subheader("🔍 연예인 쇼핑 키워드 탐색")
    
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])
    
    with filter_col1:
        selected_cat = st.selectbox("1차 카테고리", ["전체"] + list(CATEGORY_STRUCTURE.keys()), key="cat_select")
        
    with filter_col2:
        if selected_cat == "전체":
            sub_options = ["전체"] + [item for sublist in CATEGORY_STRUCTURE.values() for item in sublist]
        else:
            sub_options = ["전체"] + CATEGORY_STRUCTURE[selected_cat]
        selected_sub = st.selectbox("2차 세부 인물/테마", sub_options, key="sub_select")

    with filter_col3:
        search_query = st.text_input("제목 / 채널명 / 인물명 통합 검색", "", key="search_input")

    # 태그형 칩(Chip) UI
    st.write("📌 **빠른 퀵 트렌드 칩 (Chip)**")
    chip_cols = st.columns(7)
    quick_chips = ["전체", "#장원영", "#카리나", "#프리지아", "#김나영", "#공항패션", "#내돈내산"]
    
    for idx, chip in enumerate(quick_chips):
        with chip_cols[idx]:
            label = chip if chip != "전체" else "🔄 전체보기"
            if st.button(label, key=f"chip_btn_{idx}"):
                st.session_state.selected_chip = None if chip == "전체" else chip.replace("#", "")

    if st.session_state.selected_chip:
        st.caption(f"현재 선택된 칩 필터: **#{st.session_state.selected_chip}**")

    # --- 통합 데이터 필터링 로직 ---
    filtered_df = df.copy()

    # 1. 1차/2차 카테고리 선택 연동
    if selected_sub != "전체":
        filtered_df = filtered_df[
            (filtered_df['keyword'] == selected_sub) |
            (filtered_df['title'].str.contains(selected_sub, case=False, na=False))
        ]
    elif selected_cat != "전체":
        cat_targets = CATEGORY_STRUCTURE[selected_cat]
        pattern = "|".join(cat_targets)
        filtered_df = filtered_df[
            (filtered_df['keyword'].isin(cat_targets)) |
            (filtered_df['title'].str.contains(pattern, case=False, na=False))
        ]

    # 2. 퀵 칩 선택 연동
    if st.session_state.selected_chip:
        filtered_df = filtered_df[
            (filtered_df['keyword'] == st.session_state.selected_chip) |
            (filtered_df['title'].str.contains(st.session_state.selected_chip, case=False, na=False))
        ]

    # 3. 직접 검색창 입력 연동 (제목, 채널명, 키워드 유연 매칭)
    if search_query.strip():
        query = search_query.strip()
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(query, case=False, na=False) |
            filtered_df['channel_title'].str.contains(query, case=False, na=False) |
            filtered_df['keyword'].str.contains(query, case=False, na=False)
        ]

    # 4. 조회수 내림차순 정렬 (높은 조회수 순)
    sorted_df = filtered_df.sort_values(by="view_count", ascending=False)

    st.divider()
    st.subheader(f"🔥 인기 연예인 쇼핑 쇼츠 ({len(sorted_df)}건)")

    # 4열 카드 그리드 출력
    if not sorted_df.empty:
        cols_per_row = 4
        rows = [sorted_df.iloc[i:i+cols_per_row] for i in range(0, len(sorted_df), cols_per_row)]

        for row in rows:
            grid_cols = st.columns(cols_per_row)
            for idx, (_, item) in enumerate(row.iterrows()):
                with grid_cols[idx]:
                    video_url = f"https://www.youtube.com/shorts/{item['video_id']}"
                    views_count = item['view_count']
                    views_formatted = f"{views_count/10000:.1f}만회" if views_count >= 10000 else f"{views_count:,}회"
                    
                    st.markdown(f"""
                        <a href="{video_url}" target="_blank" style="text-decoration: none;">
                            <div class="shorts-card">
                                <div class="img-container">
                                    <img src="{item['thumbnail_url']}" class="shorts-img" alt="{item['title']}">
                                </div>
                                <div class="card-content">
                                    <div class="card-title">{item['title']}</div>
                                    <div class="card-info">
                                        <span class="channel-name">@{item['channel_title']}</span>
                                        <span class="view-badge">👀 {views_formatted}</span>
                                    </div>
                                </div>
                            </div>
                        </a>
                    """, unsafe_allow_html=True)
    else:
        st.warning("조건에 맞는 연예인 쇼핑 쇼츠가 없습니다.")
else:
    st.info("데이터가 없습니다.")
