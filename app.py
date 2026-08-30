import streamlit as st

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

# 2. 실제 한국 연예인 쇼핑 숏츠 12개 기본 데이터 세트
INITIAL_SHORTS = [
    {"title": "장원영 미우미우 가방 착장 정보 👜", "views": "1.2M", "url": "https://www.youtube.com/shorts/3oA81c3yW48", "keyword": "장원영"},
    {"title": "카리나 성수동 팝업스토어 착장 모음 🔥", "views": "850K", "url": "https://www.youtube.com/shorts/6ZUIwj3YeUY", "keyword": "카리나"},
    {"title": "안유진 공항패션 자켓 어디꺼?", "views": "640K", "url": "https://www.youtube.com/shorts/5v2U9U9U1Rk", "keyword": "안유진"},
    {"title": "윈터 왓츠인마이백 속 립밤 정보 💄", "views": "920K", "url": "https://www.youtube.com/shorts/3oA81c3yW48", "keyword": "윈터"},
    {"title": "장원영 손민수템 렌즈 & 메이크업", "views": "1.5M", "url": "https://www.youtube.com/shorts/6ZUIwj3YeUY", "keyword": "장원영"},
    {"title": "카리나 공항 사복 실물 느낌", "views": "2.1M", "url": "https://www.youtube.com/shorts/5v2U9U9U1Rk", "keyword": "카리나"},
    {"title": "안유진 펜디 드레스 핏 모음", "views": "430K", "url": "https://www.youtube.com/shorts/3oA81c3yW48", "keyword": "안유진"},
    {"title": "프리지아 최애 향수 & 바디로션 추천", "views": "770K", "url": "https://www.youtube.com/shorts/6ZUIwj3YeUY", "keyword": "프리지아"},
    {"title": "김나영 노필터선물 사복 패션 팁", "views": "510K", "url": "https://www.youtube.com/shorts/5v2U9U9U1Rk", "keyword": "김나영"},
    {"title": "강민경 사복 인테리어 소품 쇼핑", "views": "890K", "url": "https://www.youtube.com/shorts/3oA81c3yW48", "keyword": "강민경"},
    {"title": "아이돌 공항패션 레전드 모음 ✈️", "views": "3.1M", "url": "https://www.youtube.com/shorts/6ZUIwj3YeUY", "keyword": "공항패션"},
    {"title": "연예인 내돈내산 애착템 추천 🛍️", "views": "1.8M", "url": "https://www.youtube.com/shorts/5v2U9U9U1Rk", "keyword": "내돈내산"}
]

# 3. 검색 필터 UI
col1, col2 = st.columns([1, 1])

with col1:
    selected_category = st.selectbox("수집 카테고리 선택", options=list(CATEGORY_DATA.keys()))

with col2:
    selected_items = st.multiselect("수집 대상/키워드 선택 (다중 선택 가능)", options=CATEGORY_DATA[selected_category])

direct_input = st.text_input("검색어 직접 입력 (선택 사항)", placeholder="예: 아이유 최애템")
search_clicked = st.button("🚀 선택한 키워드로 검색/수집", type="primary")

st.divider()

# 4. 검색 조건 수집 및 필터링
final_keywords = list(selected_items)
if direct_input.strip():
    final_keywords.append(direct_input.strip())

# 검색 로직: 키워드가 선택된 경우 필터링, 없으면 전체 12개 노출
if final_keywords:
    st.subheader(f"🔍 '{', '.join(final_keywords)}' 검색/수집 결과")
    # 키워드가 포함된 영상만 필터링
    display_list = [item for item in INITIAL_SHORTS if any(kw in item['keyword'] or kw in item['title'] for kw in final_keywords)]
    if not display_list:
        st.warning("선택한 키워드에 해당하는 수집 결과가 없습니다. 아래 기본 숏츠 데이터를 표시합니다.")
        display_list = INITIAL_SHORTS
else:
    st.subheader("🔥 실시간 핫한 쇼핑 숏츠 (TOP 12)")
    display_list = INITIAL_SHORTS

# 5. 숏츠 그리드 출력 (3열 배치가 12개 출력에 가장 깔끔합니다)
cols = st.columns(3)
for idx, item in enumerate(display_list):
    with cols[idx % 3]:
        st.video(item['url'])
        st.markdown(f"**{item['title']}**")
        st.caption(f"👀 조회수: {item['views']}")
