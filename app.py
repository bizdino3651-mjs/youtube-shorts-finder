import streamlit as st
import random  # 실제 API 연동 시 백엔드 데이터로 대체

st.set_page_config(page_title="유튜브 쇼핑 숏츠 수집기", layout="wide")

st.title("⚡ 유튜브 쇼핑 숏츠 수집기")
st.caption("카테고리별 인물 및 쇼핑 키워드를 선택하여 숏츠 데이터를 수집하세요.")

# 1. 카테고리 데이터
CATEGORY_DATA = {
    "🔥 인기 아이돌": ["장원영", "카리나", "안유진", "윈터"],
    "💄 패션/뷰티 인플루언서": ["프리지아", "이사배"],
    "⭐ 셀럽 / 라이프스타일": ["김나영", "강민경"],
    "🛍️ 쇼핑 테마 키워드": ["공항패션", "내돈내산", "왓츠인마이백"]
}

# 2. 상단 검색 및 필터 UI
col1, col2 = st.columns([1, 1])

with col1:
    selected_category = st.selectbox(
        "수집 카테고리 선택",
        options=list(CATEGORY_DATA.keys())
    )

with col2:
    selected_items = st.multiselect(
        "수집 대상/키워드 선택 (다중 선택 가능)",
        options=CATEGORY_DATA[selected_category]
    )

direct_input = st.text_input("검색어 직접 입력 (선택 사항)", placeholder="예: 아이유 최애템")

# 검색 상태 처리
search_clicked = st.button("🚀 선택한 키워드로 검색/수집", type="primary")

st.divider()

# 3. 숏츠 임베드 및 카드 출력용 모의 데이터 (실제 연동 시 YouTube API/CSV 데이터로 대체)
MOCK_HOT_SHORTS = [
    {"title": "장원영 인스타그램 속 그 가방 정보 👜", "views": "1.2M", "video_id": "dQw4w9WgXcQ"},
    {"title": "카리나 성수동 팝업스토어 착장 모음 🔥", "views": "850K", "video_id": "3JZ_D3ELwOQ"},
    {"title": "안유진 공항패션 자켓 어디꺼?", "views": "640K", "video_id": "L_jWHffIx5E"},
]

# 4. 결과 출력 영역
final_keywords = list(selected_items)
if direct_input.strip():
    final_keywords.append(direct_input.strip())

if search_clicked and final_keywords:
    st.subheader(f"🔍 '{', '.join(final_keywords)}' 검색 결과")
    st.info(f"선택한 키워드 기준 수집 결과입니다.")
else:
    st.subheader("🔥 실시간 핫한 쇼핑 숏츠")
    st.caption("현재 가장 인기 있는 연예인 쇼핑 숏츠 목록입니다.")

# 5. 영상 카드를 3열 그리드로 표시
cols = st.columns(3)
for idx, item in enumerate(MOCK_HOT_SHORTS):
    with cols[idx % 3]:
        # 유튜브 숏츠 임베드 플레이어
        st.video(f"https://www.youtube.com/watch?v={item['video_id']}")
        st.markdown(f"**{item['title']}**")
        st.caption(f"👀 조회수: {item['views']}")
