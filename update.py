import pandas as pd
import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from PublicDataReader import TransactionPrice

st.set_page_config(layout="wide")

# 서비스 키 초기화 및 API 설정
service_key = "pII%2BrqHs3TfQwKgsYX%2Fx7fJuQiml0eppEVSKFnXO%2BJ4DgrCY53X9tKkMZaS4%2FbOTcfYEOfq3WtZoeONMjs3nPw%3D%3D"
api = TransactionPrice(service_key)

# 시군구 코드를 조회하는 함수
def fetch_region_code(location_name):
    """법정동명을 사용하여 지역 코드를 조회하고 앞의 5자리를 정수로 반환하는 함수"""
    encoded_location_name = quote(location_name)
    url = f"http://apis.data.go.kr/1741000/StanReginCd/getStanReginCdList?serviceKey={service_key}&pageNo=1&numOfRows=3&type=xml&locatadd_nm={encoded_location_name}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            region_cd_element = root.find('.//region_cd')
            if region_cd_element is not None:
                five_digit_region_code = region_cd_element.text[:5]
                return int(five_digit_region_code)
            else:
                st.error("Region code not found in the response.")
        except ET.ParseError:
            st.error("Failed to parse XML")
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
    return None

# 스트림릿 사이드바 설정
property_type = st.sidebar.selectbox("Property Type", ["아파트", "연립다세대", "단독/다가구"])
trade_type = st.sidebar.selectbox("Trade Type", ["매매", "전세", "월세"])
location_name = st.sidebar.text_input("Enter Region Name")

# 사용자가 지역명을 입력하면 시군구 코드 조회
if location_name:
    sigungu_code = fetch_region_code(location_name)
    if sigungu_code:
        st.sidebar.write(f"Sigungu Code: {sigungu_code}")
    else:
        sigungu_code = None
else:
    sigungu_code = None

start_year_month = st.sidebar.text_input("Start Year-Month", "202201")
end_year_month = st.sidebar.text_input("End Year-Month", "202212")

if sigungu_code:
    # 기간 내 조회
    df = api.get_data(
        property_type=property_type,
        trade_type=trade_type,
        sigungu_code=str(sigungu_code),
        start_year_month=start_year_month,
        end_year_month=end_year_month,
    )
    # 선택된 열만 포함하는 새로운 데이터프레임 생성
    if not df.empty:
        df = df[['지역코드', '도로명', '법정동', '지번', '아파트', '층', '전용면적', '월', '거래금액']]
    # 페이지네이션
    page_size = 100
    total_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)
    page_number = st.sidebar.number_input('Page Number', min_value=1, max_value=total_pages, value=1)
    start_row = (page_number - 1) * page_size
    end_row = start_row + page_size
    st.dataframe(df.iloc[start_row:end_row], width=2800, height=1900)
else:
    st.write("Please enter a valid region name to fetch data.")

# 스트림릿 앱 실행을 위한 명령
# streamlit run update.py
