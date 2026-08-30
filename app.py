import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="유튜브 쇼츠 골든파인더 트렌드",
    layout="wide",
    page_icon="🎬"
)

# --- CSS 스타일링 (검은 여백 완벽 제거 및 가운데 쇼츠 화면만 꽉 채우기) ---
st.markdown("""
    <style>
    /* 카드 전체 레이아웃 (유튜브 Shorts UI 스타일) */
    .card {
        margin-bottom: 24px;
        background-color: transparent;
        transition: transform 0.15s ease-in-out;
        cursor: pointer;
        display: flex;
        flex-direction: column;
    }
    
    .card:hover {
        transform: translateY(-4px);
    }
    
    /* 9:16 비율 세로 썸네일 프레임 (모서리 둥글게) */
    .card-img-wrapper {
        width: 100%;
        aspect-ratio: 9 / 16;
        border-radius: 12px;
        overflow: hidden;
        background-color: #000000;
        position: relative;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* 💥 마법의 CSS: 검은 여백을 프레임 밖으로 완전히 잘라내고 가운데 쇼츠만 꽉 채우기 */
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center center;
        /* 유튜브 썸네일 특유의 좌우/위아래 검은 레터박스를 정밀하게 크롭하여 밀어냄 */
        transform: scaleX(3.1) scaleY(1.75);
        display: block;
    }
    
    /* 카드 하단 정보 영역 */
    .card-body {
        padding-top: 10px;
    }
    
    .card-title {
        font-size: 14px;
        font-weight: 600;
        color: #0f0f0f;
        display: -webkit-box;
        -webkit-line-clamp: 2; /* 2줄까지만 표시 */
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        height: 38px;
        line-height: 1.35;
        margin-bottom: 4px;
    }
    
    .card-meta {
        font-size: 13px;
        color: #606060;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .card-views {
        font-weight: 400;
        color: #606060;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 유튜브 쇼츠 골든파인더 트렌드")

filename = "shorts_history.csv"

if os.path.exists(filename):
    df = pd.read_csv(filename)
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # 썸네일 기본 주소 생성
        df['thumbnail_url'] = df['video_id'].apply(lambda x: f"https://img.youtube.com/vi/{x}/hqdefault.jpg")

    # --- 1. 통계 요약 (상단 대시보드) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 수집 쇼츠", f"{len(df)}개")
    col2.metric("수집 키워드", f"{df['keyword'].nunique()}개" if not df.empty else "0개")
    if not df.empty:
        top_view = df.sort_values(by="view_count", ascending=False).iloc[0]
        col3.metric("최고 조회수", f"{top_view['view_count']/10000:.1f}만회")
        col4.metric("마지막 수집 시각", df['timestamp'].max().strftime('%m/%d %H:%M'))

    st.divider()

    # --- 2. 검색 및 필터 ---
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        keywords = ["전체"] + (list(df['keyword'].unique()) if not df.empty else [])
        selected_kw = st.selectbox("수집 키워드 선택", keywords)
        
    with filter_col2:
        search_query = st.text_input("제목 / 채널명 직접 검색", "")

    filtered_df = df if selected_kw == "전체" else df[df['keyword'] == selected_kw]

    if search_query.strip():
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['channel_title'].str.contains(search_query, case=False, na=False)
        ]

    sorted_df = filtered_df.sort_values(by="view_count", ascending=False)

    st.subheader(f"🔥 인기 쇼츠 그리드 ({len(sorted_df)}건)")

    # --- 3. 5열 반응형 그리드 ---
    if not sorted_df.empty:
        cols_per_row = 5
        rows = [sorted_df.iloc[i:i+cols_per_row] for i in range(0, len(sorted_df), cols_per_row)]

        for row in rows:
            grid_cols = st.columns(cols_per_row)
            for idx, (_, item) in enumerate(row.iterrows()):
                with grid_cols[idx]:
                    video_url = f"https://www.youtube.com/shorts/{item['video_id']}"
                    
                    # 조회수 단위 표기 (조회수 OO만회)
                    views_count = item['view_count']
                    if views_count >= 10000:
                        views_formatted = f"조회수 {views_count/10000:.1f}만회"
                    else:
                        views_formatted = f"조회수 {views_count:,}회"
                    
                    st.markdown(f"""
                        <a href="{video_url}" target="_blank" style="text-decoration: none;">
                            <div class="card">
                                <div class="card-img-wrapper">
                                    <img src="{item['thumbnail_url']}" class="card-img" alt="{item['title']}">
                                </div>
                                <div class="card-body">
                                    <div class="card-title">{item['title']}</div>
                                    <div class="card-meta">
                                        <span class="card-views">{views_formatted}</span>
                                    </div>
                                </div>
                            </div>
                        </a>
                    """, unsafe_allow_html=True)
    else:
        st.warning("검색 조건에 맞는 쇼츠 영상이 없습니다.")

else:
    st.info("아직 수집된 데이터(shorts_history.csv)가 없습니다.")
