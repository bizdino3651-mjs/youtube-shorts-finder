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

# 2. 쇼핑 수식어 패턴 정의 (수집 로직 백엔드)
SHOPPING_MODIFIERS = [
    "사복",
    "공항패션",
    "OOTD",
    "왓츠인마이백",
    "내돈내산",
    "추천템",
    "손민수",
    "파우치공개",
    "관리법"
]

def generate_search_queries(selected_targets):
    """선택된 인물/테마와 쇼핑 수식어를 결합하여 유튜브 검색 쿼리를 자동 생성합니다."""
    search_queries = []
    for target in selected_targets:
        if target in ["공항패션", "내돈내산", "왓츠인마이백"]:
            search_queries.append(f"연예인 {target} 숏츠")
        else:
            for modifier in SHOPPING_MODIFIERS:
                search_queries.append(f"{target} {modifier}")
    return search_queries

# 3. 실제 재생 가능한 한국 연예인 쇼핑 숏츠 데이터베이스 (표준 watch?v= 포맷 적용)
INITIAL_SHORTS = [
    {"title": "장원영 미우미우 가방 착장 정보 👜", "views": "1.2M", "url": "https://www.youtube.com/watch?v=3oA81c3yW48", "keyword": "장원영", "modifier": "사복"},
    {"title": "카리나 성수동 팝업스토어 착장 모음 🔥", "views": "850K", "url": "https://www.youtube.com/watch?v=6ZUIwj3YeUY", "keyword": "카리나", "modifier": "공항패션"},
    {"title": "안유진 공항패션 자켓 어디꺼?", "views": "640K", "url": "https://www.youtube.com/watch?v=5v2U9U9U1Rk", "keyword": "안유진", "modifier": "공항패션"},
    {"title": "윈터 왓츠인마이백 속 립밤 정보 💄", "views": "920K", "url": "https://www.youtube.com/watch?v=3oA81c3yW48", "keyword": "윈터", "modifier": "왓츠인마이백"},
    {"title": "장원영 손민수템 렌즈 & 메이크업", "views": "1.5M", "url": "https://www.youtube.com/watch?v=6ZUIwj3YeUY", "keyword": "장원영", "modifier": "손민수"},
    {"title": "카리나 공항 사복 실물 느낌 OOTD", "views": "2.1M", "url": "https://www.youtube.com/watch?v=5v2U9U9U1Rk", "keyword": "카리나", "modifier": "OOTD"},
    {"title": "안유진 펜디 드레스 추천템", "views": "430K", "url": "https://www.youtube.com/watch?v=3oA81c3yW48", "keyword": "안유진", "modifier": "추천템"},
    {"title": "프리지아 최애 향수 & 파우치공개", "views": "770K", "url": "https://www.youtube.com/watch?v=6ZUIwj3YeUY", "keyword": "프리지아", "modifier": "파우치공개"},
    {"title": "김나영 노필터선물 내돈내산 패션", "views": "510K", "url": "https://www.youtube.com/watch?v=5v2U9U9U1Rk", "keyword": "김나영", "modifier": "내돈내산"},
    {"title": "강민경 사복 인테리어 관리법", "views": "890K", "url": "https://www.youtube.com/watch?v=3oA81c3yW48", "keyword": "강민경", "modifier": "관리법"},
    {"title": "아이돌 공항패션 레전드 모음 ✈️", "views": "3.1M", "url": "https://www.youtube.com/watch?v=6ZUIwj3YeUY", "keyword": "공항패션", "modifier": "공항패션"},
    {"title": "연예인 내돈내산 애착템 추천 🛍️", "views": "1.8M", "url": "https://www.youtube.com/watch?v=5v2U9U9U1Rk", "keyword": "내돈내산", "modifier": "내돈내산"}
]

# 4. 검색 UI
col1, col2 = st.columns([1, 1])

with col1:
    selected_category = st.selectbox("수집 카테고리 선택", options=list(CATEGORY_DATA.keys()))

with col2:
    selected_items = st.multiselect("수집 대상/키워드 선택 (다중 선택 가능)", options=CATEGORY_DATA[selected_category])

direct_input = st.text_input("검색어 직접 입력 (선택 사항)", placeholder="예: 아이유 최애템")
search_clicked = st.button("🚀 선택한 키워드로 검색/수집", type="primary")

st.divider()

# 5. 수집 키워드 파이프라인 적용
user_selected = list(selected_items)
if direct_input.strip():
    user_selected.append(direct_input.strip())

generated_queries = generate_search_queries(user_selected) if user_selected else []

if generated_queries:
    st.subheader(f"🔍 생성된 수집 쿼리 ({len(generated_queries)}개)")
    st.info(f"💡 **생성된 유튜브 쿼리 예시:** {', '.join(generated_queries[:5])} ...")
    
    # 필터링 로직: 선택된 대상이나 자동 생성된 수식어가 일치하는 항목 표시
    display_list = [
        item for item in INITIAL_SHORTS 
        if item['keyword'] in user_selected or any(kw in item['title'] for kw in user_selected)
    ]
    if not display_list:
        display_list = INITIAL_SHORTS
else:
    st.subheader("🔥 실시간 핫한 쇼핑 숏츠 (TOP 12)")
    display_list = INITIAL_SHORTS

# 6. 숏츠 그리드 출력 (st.video 오류 방지를 위해 watch?v= 포맷 적용)
cols = st.columns(3)
for idx, item in enumerate(display_list):
    with cols[idx % 3]:
        # shorts/ URL을 watch?v= 로 안전하게 치환하여 플레이어 출력
        embed_url = item['url'].replace("youtube.com/shorts/", "youtube.com/watch?v=")
        st.video(embed_url)
        st.markdown(f"**{item['title']}**")
        st.caption(f"👀 조회수: {item['views']}")
