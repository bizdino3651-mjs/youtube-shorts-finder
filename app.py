import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="유튜브 쇼핑 숏츠 수집기", layout="wide")

st.title("⚡ 유튜브 쇼핑 숏츠 수집기")
st.caption("카테고리별 인물 및 쇼핑 키워드를 선택하여 숏츠 데이터를 수집하세요.")

# 1. 카테고리별 키워드 데이터 정의
CATEGORY_DATA = {
    "🔥 인기 아이돌": ["장원영", "카리나", "안유진", "윈터"],
    "💄 패션/뷰티 인플루언서": ["프리지아", "이사배"],
    "⭐ 셀럽 / 라이프스타일": ["김나영", "강민경"],
    "🛍️ 쇼핑 테마 키워드": ["공항패션", "내돈내산", "왓츠인마이백"]
}

# 세션 상태 초기화 (선택된 태그 저장용)
if "selected_tags" not in st.session_state:
    st.session_state.selected_tags = []

# 2. UI 레이아웃 구성
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 수집 카테고리 선택")
    # 카테고리 드롭다운
    selected_category = st.selectbox(
        "카테고리를 선택하세요",
        options=list(CATEGORY_DATA.keys())
    )

with col2:
    st.subheader("2. 세부 대상/키워드 선택")
    # 선택한 카테고리에 맞는 세부 항목 드롭다운 (멀티 선택 가능)
    available_options = CATEGORY_DATA[selected_category]
    selected_items = st.multiselect(
        "수집할 인물 또는 키워드를 선택하세요 (다중 선택 가능)",
        options=available_options,
        default=[]
    )

# 3. 직접 입력 영역
st.divider()
direct_input = st.text_input("검색어 직접 입력 (선택 사항)", placeholder="예: 아이브 사복, 에스파 메이크업")

# 4. 수집 실행 버튼 및 파라미터 전달
st.divider()

if st.button("🚀 선택한 키워드로 수집 시작", type="primary"):
    # 최종 수집 대상 리스트 정리
    final_keywords = list(selected_items)
    if direct_input.strip():
        final_keywords.append(direct_input.strip())
        
    if not final_keywords:
        st.warning("수집할 키워드를 하나 이상 선택하거나 입력해주세요.")
    else:
        st.success(f"수집을 시작합니다! 선택된 키워드: **{', '.join(final_keywords)}**")
        
        # TODO: collect.py의 수집 함수 호출 부분
        # import collect
        # collect.run_collection(final_keywords)
