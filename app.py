import streamlit as st
import requests
from dotenv import load_dotenv
import os

FOSSA_API_URL = "https://api.fossa.com"

# 프로젝트 설정 페이지
def project_setup():
    st.title("프로젝트 설정")
    
    # .env 파일에서 FOSSA_API_KEY 불러오기
    load_dotenv()
    FOSSA_API_KEY = os.getenv("FOSSA_API_KEY")

    # Streamlit secrets에서 FOSSA_API_KEY 불러오기
    if not FOSSA_API_KEY:
        FOSSA_API_KEY = st.secrets.get("FOSSA_API_KEY")

    # FOSSA_API_KEY가 없는 경우 사용자로부터 직접 입력받기
    if not FOSSA_API_KEY:
        FOSSA_API_KEY = st.text_input("FOSSA API KEY를 입력하세요", type="password")
        if not FOSSA_API_KEY:
            st.warning("FOSSA API KEY를 입력해주세요.")
            return

    project_name = st.text_input("프로젝트 이름", value="My Open Source Project")
    project_folder = st.text_input("프로젝트 폴더 경로", value="/path/to/project")
    scan_options = st.multiselect("검사 옵션", ["라이선스 검사", "스니펫 분석"])
    
    if st.button("프로젝트 검사"):
        # 프로젝트 폴더 검사 실행
        response = requests.post(f"{FOSSA_API_URL}/api/cli/analyze", headers={
            "Authorization": f"Bearer {FOSSA_API_KEY}"
        }, json={
            "name": project_name,
            "path": project_folder,
            "scanOptions": scan_options
        })
        if response.status_code == 200:
            st.success("프로젝트 검사가 성공적으로 완료되었습니다.")
        else:
            st.error("프로젝트 검사에 실패했습니다.")

    return FOSSA_API_KEY

# 검사 결과 확인 페이지
def scan_results(FOSSA_API_KEY):
    st.title("검사 결과")
    project_id = st.text_input("프로젝트 ID")
    if st.button("결과 확인"):
        # 검사 결과를 FOSSA API에서 가져오는 API 호출
        response = requests.get(f"{FOSSA_API_URL}/api/projects/{project_id}/latest-scan", headers={
            "Authorization": f"Bearer {FOSSA_API_KEY}"
        })
        if response.status_code == 200:
            results = response.json()
            # 검사 결과 표시
            st.subheader("라이선스 검사 결과")
            st.write(results["licenseScan"])
            st.subheader("스니펫 분석 결과")
            st.write(results["snippetAnalysis"])
        else:
            st.error("검사 결과를 가져오는데 실패했습니다.")

# 대시보드 페이지
def dashboard(FOSSA_API_KEY):
    st.title("대시보드")
    # 대시보드에 필요한 데이터를 FOSSA API에서 가져오는 API 호출
    response = requests.get(f"{FOSSA_API_URL}/api/projects", headers={
        "Authorization": f"Bearer {FOSSA_API_KEY}"
    })
    if response.status_code == 200:
        data = response.json()
        # 대시보드 데이터 시각화
        st.subheader("프로젝트 현황")
        st.bar_chart(data["projectStats"])
        st.subheader("라이선스 위반 현황")
        st.pie_chart(data["licenseViolations"])
    else:
        st.error("대시보드 데이터를 가져오는데 실패했습니다.")

def main():
    st.title("M.AI.Snippet Analyzer")

    FOSSA_API_KEY = None

    # 사이드바 메뉴
    sidebar_options = ["프로젝트 설정", "검사 결과", "대시보드"]
    selected_option = st.sidebar.selectbox("메뉴", sidebar_options)

    # 선택한 메뉴에 따라 해당 페이지 표시
    if selected_option == "프로젝트 설정":
        FOSSA_API_KEY = project_setup()
    elif selected_option == "검사 결과":
        scan_results(FOSSA_API_KEY)
    elif selected_option == "대시보드":
        dashboard(FOSSA_API_KEY)

if __name__ == "__main__":
    main()