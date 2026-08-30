import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="유튜브 쇼츠 트렌드 대시보드",
    layout="wide",
    page_icon="🎬"
)

# --- 트렌디한 모던 카드 UI 스타일링 ---
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 세팅 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 모던 카드 디자인 */
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
    
    /* 썸네일 컨테이너: 원본 비율 유지 */
    .img-container {
        width: 100%;
        position: relative;
        background-color: #000000;
        overflow: hidden;
    }
    
    .shorts-img {
        width: 100%;
        height: auto;
        display: block;
        object-fit: contain;
    }
    
    /* 콘텐츠 영역 */
    .card-content {
        padding: 14px 16px;
    }
    
    .card-title {
        font-size: 14px;
        font-weight: 700;
        color: #212529;
        line-height: 1.4;
        height: 40px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        margin-bottom: 10px;
    }
    
    .card-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #6c757d;
    }
    
    .view-badge {
        background-color: #fff0f1;
        color: #ff0033;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
    }
    
    .channel-name {
        font-weight: 500;
        max-width: 110px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 유튜브 쇼츠 골든파인더 트렌드")

filename = "shorts_history.csv"

if os.path.exists(filename):
    df = pd.read_csv(filename)
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['thumbnail_url'] = df['video_id'].apply(lambda x: f"https://img.youtube.com/vi/{x}/hqdefault.jpg")

    # 상단 요약 통계
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 수집 쇼츠", f"{len(df)}개")
    col2.metric("수집 키워드", f"{df['keyword'].nunique()}개" if not df.empty else "0개")
    if not df.empty:
        top_view = df.sort_values(by="view_count", ascending=False).iloc[0]
        col3.metric("최고 조회수", f"{top_view['view_count']/10000:.1f}만회")
        col4.metric("최근 업데이트", df['timestamp'].max().strftime('%m/%d %H:%M'))

    st.divider()

    # 검색 및 필터
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

    st.subheader(f"🔥 실시간 인기 쇼츠 ({len(sorted_df)}건)")

    # 4열 모던 카드 그리드
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
        st.warning("조건에 맞는 쇼츠가 없습니다.")
else:
    st.info("데이터가 없습니다.")
