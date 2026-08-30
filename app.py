import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="유튜브 쇼츠 골든파인더 트렌드",
    layout="wide",
    page_icon="🎬"
)

# --- 골든파인더 스타일 CSS (세로형 9:16 비율 및 반응형 그리드) ---
st.markdown("""
    <style>
    /* 카드 전체 레이아웃 */
    .card {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        background-color: #ffffff;
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-6px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    }
    /* 9:16 세로 비율 썸네일 */
    .card-img-wrapper {
        width: 100%;
        aspect-ratio: 9 / 16;
        overflow: hidden;
        background-color: #000000;
        position: relative;
    }
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    /* 카드 텍스트 정보 영역 */
    .card-body {
        padding: 12px;
    }
    .card-title {
        font-size: 13px;
        font-weight: 600;
        color: #1a1a1a;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        height: 36px;
        line-height: 1.35;
        margin-bottom: 8px;
    }
    .card-meta {
        font-size: 11px;
        color: #777777;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-channel {
        font-weight: bold;
        color: #FF0000;
        max-width: 60%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-views {
        font-weight: 600;
        color: #333333;
    }
    </style>
""", unsafe_allow_stdio=True)

st.title("🎬 유튜브 쇼츠 골든파인더 트렌드")

filename = "shorts_history.csv"

if os.path.exists(filename):
    df = pd.read_csv(filename)
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # 세로형 9:16 크롭용 high quality 썸네일 URL 지정
        df['thumbnail_url'] = df['video_id'].apply(lambda x: f"https://img.youtube.com/vi/{x}/hqdefault.jpg")

    # --- 1. 통계 요약 (상단 대시보드) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 수집 쇼츠", f"{len(df)}개")
    col2.metric("수집 키워드", f"{df['keyword'].nunique()}개" if not df.empty else "0개")
    if not df.empty:
        top_view = df.sort_values(by="view_count", ascending=False).iloc[0]
        col3.metric("최고 조회수", f"{top_view['view_count']/10000:.1f}만회")
        col4.metric("최근 업데이트", df['timestamp'].max().strftime('%m/%d %H:%M'))

    st.divider()

    # --- 2. 수집 키워드 선택 및 제목/채널명 직접 검색 ---
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        keywords = ["전체"] + (list(df['keyword'].unique()) if not df.empty else [])
        selected_kw = st.selectbox("수집 키워드 선택", keywords)
        
    with filter_col2:
        search_query = st.text_input("제목 / 채널명 직접 검색", "")

    # 필터링 로직
    filtered_df = df if selected_kw == "전체" else df[df['keyword'] == selected_kw]

    if search_query.strip():
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['channel_title'].str.contains(search_query, case=False, na=False)
        ]

    # 조회수 높은 순서 정렬
    sorted_df = filtered_df.sort_values(by="view_count", ascending=False)

    st.subheader(f"🔥 인기 쇼츠 그리드 ({len(sorted_df)}건)")

    # --- 3. 반응형 4열 세로 썸네일 그리드 구현 ---
    if not sorted_df.empty:
        cols_per_row = 4
        rows = [sorted_df.iloc[i:i+cols_per_row] for i in range(0, len(sorted_df), cols_per_row)]

        for row in rows:
            grid_cols = st.columns(cols_per_row)
            for idx, (_, item) in enumerate(row.iterrows()):
                with grid_cols[idx]:
                    video_url = f"https://www.youtube.com/shorts/{item['video_id']}"
                    
                    # 조회수 단위 표기 (만 단위)
                    views_count = item['view_count']
                    if views_count >= 10000:
                        views_formatted = f"{views_count/10000:.1f}만회"
                    else:
                        views_formatted = f"{views_count:,}회"
                    
                    # 세로형 9:16 카드 렌더링
                    st.markdown(f"""
                        <a href="{video_url}" target="_blank" style="text-decoration: none;">
                            <div class="card">
                                <div class="card-img-wrapper">
                                    <img src="{item['thumbnail_url']}" class="card-img" alt="{item['title']}">
                                </div>
                                <div class="card-body">
                                    <div class="card-title">{item['title']}</div>
                                    <div class="card-meta">
                                        <span class="card-channel">@{item['channel_title']}</span>
                                        <span class="card-views">👀 {views_formatted}</span>
                                    </div>
                                </div>
                            </div>
                        </a>
                    """, unsafe_allow_stdio=True)
    else:
        st.warning("검색 조건에 맞는 쇼츠 영상이 없습니다.")

else:
    st.info("아직 수집된 데이터(shorts_history.csv)가 없습니다. GitHub Actions 실행 후 확인해 주세요.")
