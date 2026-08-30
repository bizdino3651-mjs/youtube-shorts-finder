import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="유튜브 쇼츠 트렌드 대시보드", layout="wide")

st.title("📱 유튜브 쇼츠 트렌드 수집 대시보드")
st.write("GitHub Actions를 통해 자동으로 수집된 유튜브 쇼츠 데이터입니다.")

filename = "shorts_history.csv"

if os.path.exists(filename):
    df = pd.read_csv(filename)
    
    # 기본 통계
    col1, col2, col3 = st.columns(3)
    col1.metric("총 수집 데이터 건수", f"{len(df)}개")
    col2.metric("수집된 키워드 수", f"{df['keyword'].nunique()}개")
    col3.metric("최근 업데이트", df['timestamp'].max() if not df.empty else "-")
    
    st.divider()
    
    # 키워드 필터
    keywords = ["전체"] + list(df['keyword'].unique())
    selected_kw = st.selectbox("검색 키워드 선택", keywords)
    
    if selected_kw != "전체":
        filtered_df = df[df['keyword'] == selected_kw]
    else:
        filtered_df = df

    # 조회수 순 정렬
    sorted_df = filtered_df.sort_values(by="view_count", ascending=False)
    
    st.subheader("📊 수집된 쇼츠 목록")
    st.dataframe(
        sorted_df,
        column_config={
            "video_id": st.column_config.LinkColumn(
                "영상 링크",
                display_text="https://www.youtube.com/watch\?v=(.*)",
                validate="^https://www.youtube.com/watch\?v=.*$"
            ),
            "view_count": st.column_config.NumberColumn("조회수", format="%d회"),
            "duration_sec": st.column_config.NumberColumn("재생시간", format="%d초")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("아직 수집된 데이터(shorts_history.csv)가 없습니다. GitHub Actions 실행 후 다시 확인해주세요.")
