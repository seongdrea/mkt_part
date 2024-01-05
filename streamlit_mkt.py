import streamlit as st
import mkt_keyword

st.set_page_config(layout="wide") #좌우로 꽉 찬 화면 구성

# 사이드바 설정
st.sidebar.title("네이버 검색순위 크롤러")
# 사이드바에 버튼 추가 (if 하고 들여쓰기 하고 사이드바에 버튼 만들면 앞으로 페이지별로 구분할 수 있다)
#if st.sidebar.button("네이버쇼핑 검색순위 크롤러"):

#본격 내용
st.title("네이버쇼핑 검색순위") # 타이틀 설정

# keyword_list를 미리 생성한다
options = ["esim",
           "일본 esim",
           "베트남 esim",
           "태국 esim",
           "대만 esim",
           "필리핀 esim",
           "미국 esim",
           "유럽 esim"
]

# 멀티셀렉트 생성
keyword_list = st.sidebar.multiselect("키워드를 선택해주세요:otter:", options, default=["esim","일본 esim","베트남 esim","태국 esim","대만 esim","필리핀 esim","미국 esim","유럽 esim"])

# 버튼을 추가.
if st.sidebar.button('크롤링 시작하기'):
    # 버튼을 클릭하면 mkt_keyword.py의 run_mkt_keyword 함수를 실행.
    for keyword in keyword_list:
        st.subheader(keyword) # 데이터프레임 제목 설정
        df = mkt_keyword.run_mkt_keyword(keyword) # 크롤링 결과가 df로 리턴되니 이걸 df에 담는다
        st.dataframe(df, width=1000, height=500)
