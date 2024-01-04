import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

naver_shopping_url = "https://shopping.naver.com/home" # 네이버 쇼핑 사이트

# 크롬 브라우저 열기
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window() #창 크기 최대화
wait = WebDriverWait(driver, 10)

keyword_list = [] #검색할 키워드 리스트변수 할당

keyword_list.append("일본 eSIM") #streamlit으로 데이터를 받아서 append 하도록 추후 변경

for keyword in keyword_list:
    # 네이버 쇼핑으로 이동
    driver.get(naver_shopping_url)
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[2]/form/div[1]/div/input"))) # 검색창 나올때까지 대기

    # 검색어 입력
    driver.find_element(By.XPATH, "/html/body/div[3]/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[2]/form/div[1]/div/input").send_keys(keyword)
    # 검색버튼 클릭
    driver.find_element(By.XPATH, "/html/body/div[3]/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[2]/form/div[1]/div/button[2]").click()
    time.sleep(5)

    # 광고 개수 구하기
    hp_contents = driver.page_source # 웹페이지 내용 가져오기
    soup = BeautifulSoup(hp_contents, 'html.parser') # BeautifulSoup을 사용하여 HTML 파싱
    divs = soup.find_all('div', class_='adProduct_price_area__yA7Ad') # 특정 class를 가진 div 태그들 찾기
    ad_cnt = len(divs) # 광고 개수!
    # 일반 상품의 마지막 행 번호
    lastprod_num = ad_cnt + 10

    # 타이틀, 가격 등의 항목들을 리스트로 만든 후 pandas에 넣기 위해 JSON으로 준비
    supplier = [] # 업체명
    price = [] # 가격
    title = [] # 상품타이틀
    zzim_cnt = [] # 찜하기 개수
    review_cnt = [] # 리뷰 수
    sales_cnt = [] # 판매개수
    is_ad = [] # 광고여부

    # 화면에 보이는 상품들 크롤링 시작
    for procedure in range(1, lastprod_num):
        print(procedure)

        # 업체명 읽기
        supplier.append(driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{}]/div/div/div[3]/div[1]/a[1]".format(procedure)).text)

        # 금액 읽기
        price.append(driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{}]/div/div/div[2]/div[2]/strong/span[1]".format(procedure)).text)

        # 상품타이틀 읽기
        title.append(driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{}]/div/div/div[2]/div[1]/a".format(procedure)).text)

        # 찜하기, 리뷰수, 구매건수는 없을수도 있으니 try-except문을 함수화 해 활용한다.
        def safe_find_element(driver, xpath):
            try:
                return driver.find_element(By.XPATH, xpath).text
            except NoSuchElementException:
                return "-"

        #엑스패스 변수할당
        ad_zzim_cnt_xpath = "/html/body/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{}]/div/div/div[2]/div[5]/span[3]/a/span/em".format(procedure)
        noad_zzim_cnt_xpath = "/html/body/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{}]/div/div/div[2]/div[5]/span[2]/a/span/em".format(procedure)
        review_cnt_xpath = "/html/body/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{}]/div/div/div[2]/div[5]/a[1]/em".format(procedure)
        sales_cnt_xpath = "/html/body/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{}]/div/div/div[2]/div[5]/a[2]/span/span/em".format(procedure)

        # 찜하기 개수 읽기 (해보니까 광고든 아니든 2개의 엘리
        try:
            zzim_cnt.append(driver.find_element(By.XPATH, ad_zzim_cnt_xpath).text)
        except:
            zzim_cnt.append(driver.find_element(By.XPATH, noad_zzim_cnt_xpath).text)

        # 리뷰 수 읽기 (광고 아닌거에만 있다)
        if procedure > ad_cnt:
            review_cnt.append(safe_find_element(driver, review_cnt_xpath))
        else:
            review_cnt.append("-")

        # 구매건수 읽기 (광고 아닌거에만 있다)
        if procedure > ad_cnt:
            sales_cnt.append(safe_find_element(driver, sales_cnt_xpath))
        else:
            sales_cnt.append("-")

        # 광고여부 표시
        is_ad.append("광고" if procedure <= ad_cnt else "-")

    print(f"업체: {len(supplier)}")
    print(f"상품명: {len(title)}")
    print(f"가격: {len(price)}")
    print(f"리뷰: {len(review_cnt)}")
    print(f"구매건수: {len(sales_cnt)}")
    print(f"찜하기: {len(zzim_cnt)}")

    # 크롤링 해온 리스트들을 데이터프레임으로 만들기
    df = pd.DataFrame({
        "업체" : supplier,
        "상품명" : title,
        "가격" : price,
        "리뷰" : review_cnt,
        "구매건수" : sales_cnt,
        "찜하기" : zzim_cnt,
        "광고여부" : is_ad
    })

# Streamlit 앱의 타이틀 설정
st.title('My Streamlit App')

# 데이터프레임 표시
st.write("Here is our DataFrame:")
st.write(df)
