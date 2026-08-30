import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="유튜브 쇼츠 골든파인더 트렌드",
    layout="wide",
    page_icon="🎬"
)

# --- CSS 스타일링 (유튜브 실제 Shorts UI 완벽 구현) ---
st.markdown("""
    <style>
    /* 카드 전체 구성 */
    .card {
        margin-bottom: 24px;
        background-color: transparent;
        transition: transform 0.15s ease-in-out;
    }
    .card:hover {
        transform: translateY(-4px);
    }
    
    /* 9:16 비율 세로 썸네일 프레임 */
    .card-img-wrapper {
        width: 100%;
        aspect-ratio: 9 / 16;
        border-radius: 12px;
        overflow: hidden;
        background-color: #000000;
        position: relative;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* 레터박스 없이 세로 프레임 전체에 꽉 채우기 */
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
        display: block;
    }
    
    /* 하단 정보 영역 (유튜브 스타일) */
    .card-body {
        padding-top: 10px;
    }
    .card-title {
        font-size: 14px;
        font-weight: 600;
        color: #0f0f0f;
        display: -webkit-box;
        -webkit-line-clamp: 2;
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
    .card-channel {
        font-weight: 500;
        color: #0f0f0f;
        font-size: 12px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 60%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 유튜브 쇼츠 골든파인더 트렌드")

filename = "shorts_history.csv"

if os.path.exists(filename):
    df = pd.read_csv(filename)
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # YouTube 고해상도 썸네일(maxresdefault) 활용, 없을 경우 기본 썸네일 대체 처리
        df['thumbnail_url'] = df['video_id'].apply(
            lambda x: f"https://i.ytimg.com/vi/{x}/maxresdefault.jpg"
        )

    # --- 1. 상단 통계 ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 수집 쇼츠", f"{len(df)}개")
    col2.metric("수집 키워드", f"{df['keyword'].nunique()}개" if not df.empty else "0개")
    if not df.empty:
        top_view = df.sort_values(by="view_count", ascending=False).iloc[0]
        col3.metric("최고 조회수", f"{top_view['view_count']/10000:.1f}만회")
        col4.metric("최근 업데이트", df['timestamp'].max().strftime('%m/%d %H:%M'))

    st.divider()

    # --- 2. 필터 및 검색 ---
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

    st.subheader(f"🔥 Shorts ({len(sorted_df)}건)")

    # --- 3. 5열 반응형 그리드 (유튜브 웹 UI 방식) ---
    if not sorted_df.empty:
        cols_per_row = 5
        rows = [sorted_df.iloc[i:i+cols_per_row] for i in range(0, len(sorted_df), cols_per_row)]

        for row in rows:
            grid_cols = st.columns(cols_per_row)
            for idx, (_, item) in enumerate(row.iterrows()):
                with grid_cols[idx]:
                    video_url = f"https://www.youtube.com/shorts/{item['video_id']}"
                    
                    # 조회수 단위 표기 (유튜브 방식: 조회수 OOO만회)
                    views_count = item['view_count']
                    if views_count >= 10000:
                        views_formatted = f"조회수 {views_count/10000:.1f}만회"
                    else:
                        views_formatted = f"조회수 {views_count:,}회"
                    
                    # 유튜브 화면과 동일한 구조의 렌더링
                    st.markdown(f"""
                        <a href="{video_url}" target="_blank" style="text-decoration: none;">
                            <div class="card">
                                <div class="card-img-wrapper">
                                    <img src="{item['thumbnail_url']}" 
                                         class="card-img" 
                                         alt="{item['title']}"
                                         onerror="this.onerror=null; this.src='https://i.ytimg.com/vi/{item['video_id']}/hqdefault.jpg';">
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
