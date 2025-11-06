"""
농작물 식별 웹앱

이미지를 업로드하거나 촬영하면 AI가 자동으로 농작물을 식별하고
상세 정보를 제공합니다.
"""

import streamlit as st
import base64
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import openai
from PIL import Image
import io


# 환경 변수 로드
load_dotenv()


# 페이지 설정
st.set_page_config(
    page_title="농작물 AI 식별기",
    page_icon="🌾",
    layout="wide"
)


def load_image_as_base64(image_bytes: bytes) -> str:
    """
    이미지 바이트를 base64로 변환합니다.
    
    Args:
        image_bytes: 이미지 바이너리 데이터
        
    Returns:
        base64 인코딩된 이미지 문자열
    """
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded_image}"


def analyze_crop_with_ai(image_base64: str, api_key: str) -> dict:
    """
    Vision API로 농작물을 분석하고 상세 정보를 받습니다.
    
    Args:
        image_base64: base64 인코딩된 이미지
        api_key: OpenAI API 키
        
    Returns:
        분석 결과 딕셔너리
    """
    client = openai.OpenAI(api_key=api_key)
    
    system_prompt = """당신은 한국의 농작물 전문가입니다.
이미지를 보고 다음 정보를 JSON 형식으로 제공하세요:

{
  "name": "농작물 한글 이름",
  "name_en": "영어 이름",
  "confidence": 0.95,
  "category": "과일/채소/곡물 등",
  "famous_regions": ["한국 내 유명 생산지1", "한국 내 유명 생산지2", "한국 내 유명 생산지3"],
  "season": "제철 시기 (예: 5월~8월)",
  "nutrition": "주요 영양소 간단 설명",
  "storage": "보관 방법 간단 설명",
  "taste": "맛 특징 간단 설명"
}

중요 규칙:
- famous_regions는 반드시 대한민국 내의 지역만 포함하세요 (예: 제주도, 나주, 충주, 영천, 김천 등)
- 한국에서 잘 재배되지 않는 작물이라도 한국에서 재배하는 지역을 찾아서 답변하세요
- 반드시 JSON 형식으로만 답변하세요
- 마크다운 코드 블록(```)은 사용하지 마세요"""

    user_prompt = """이 이미지의 농작물을 분석하고 상세 정보를 JSON으로 제공해주세요."""
    
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # 마크다운 코드 블록 제거 (```json ... ``` 형태)
        if response_text.startswith("```"):
            # 첫 번째 줄 제거 (```json)
            lines = response_text.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            # 마지막 줄 제거 (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = '\n'.join(lines).strip()
        
        # JSON 파싱
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            # JSON을 찾아서 추출 시도
            try:
                # { 부터 } 까지 추출
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_text = response_text[start_idx:end_idx+1]
                    result = json.loads(json_text)
                    return result
            except:
                pass
            
            return {"error": "JSON 파싱 실패", "raw_response": response_text, "parse_error": str(e)}
            
    except Exception as e:
        return {"error": str(e)}


def display_result(result: dict, image):
    """
    분석 결과를 예쁘게 표시합니다.
    
    Args:
        result: 분석 결과 딕셔너리
        image: 원본 이미지
    """
    if "error" in result:
        st.error(f"오류 발생: {result['error']}")
        if "raw_response" in result:
            st.code(result["raw_response"])
        return
    
    # 레이아웃: 이미지 + 결과
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption="분석된 이미지", width="stretch")
    
    with col2:
        # 농작물 이름
        st.markdown(f"## 🌱 {result.get('name', '알 수 없음')}")
        st.markdown(f"*{result.get('name_en', '')}*")
        
        # 확신도
        confidence = result.get('confidence', 0)
        st.progress(confidence)
        st.caption(f"확신도: {confidence*100:.1f}%")
        
        # 카테고리
        category = result.get('category', '-')
        st.markdown(f"**분류:** {category}")
    
    # 상세 정보 - 깔끔하게 정리
    st.markdown("---")
    
    # 유명 생산지
    regions = result.get('famous_regions', [])
    if regions:
        regions_text = ", ".join(regions)
        st.markdown(f"**🗺️ 유명 생산지:** {regions_text}")
    
    # 제철
    season = result.get('season', '-')
    st.markdown(f"**📅 제철:** {season}")
    
    # 영양 정보
    nutrition = result.get('nutrition', '-')
    st.markdown(f"**💊 영양 정보:** {nutrition}")
    
    # 보관 방법
    storage = result.get('storage', '-')
    st.markdown(f"**🏪 보관 방법:** {storage}")
    
    # 맛 특징
    taste = result.get('taste', '-')
    st.markdown(f"**👅 맛 특징:** {taste}")


def main():
    """
    메인 앱 실행 함수
    """
    # 헤더
    st.title("🌾 농작물 AI 식별기")
    st.markdown("**이미지를 업로드하면 AI가 농작물을 식별하고 상세 정보를 알려드립니다!**")
    st.markdown("---")
    
    # API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY가 설정되지 않았습니다.")
        st.info("`.env` 파일에 API 키를 설정해주세요.")
        return
    
    # 사이드바 - 사용 방법
    with st.sidebar:
        st.markdown("## 📖 사용 방법")
        st.markdown("""
        1. **이미지 업로드** 또는 **카메라 촬영**
        2. AI가 자동으로 분석
        3. 상세 정보 확인!
        """)
        
        st.markdown("---")
        st.markdown("## ℹ️ 정보")
        st.markdown("""
        - **지원 형식**: JPG, PNG
        - **분석 항목**: 
          - 농작물 이름
          - 유명 생산지
          - 제철 시기
          - 영양 정보
          - 보관 방법
          - 맛 특징
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 활용 팁")
        st.markdown("""
        - 농작물이 **선명하게** 보이는 사진
        - **가까이서** 촬영한 사진
        - **조명이 밝은** 환경에서 촬영
        """)
    
    # 이미지 입력 방법 선택
    st.markdown("## 📸 이미지 선택")
    
    input_method = st.radio(
        "입력 방법을 선택하세요:",
        ["파일 업로드", "카메라 촬영"],
        horizontal=True
    )
    
    uploaded_image = None
    
    if input_method == "파일 업로드":
        uploaded_file = st.file_uploader(
            "농작물 이미지를 업로드하세요",
            type=['jpg', 'jpeg', 'png'],
            help="JPG, PNG 형식의 이미지를 업로드할 수 있습니다."
        )
        
        if uploaded_file:
            uploaded_image = uploaded_file.read()
    
    else:  # 카메라 촬영
        camera_photo = st.camera_input("농작물 사진 촬영")
        
        if camera_photo:
            uploaded_image = camera_photo.read()
    
    # 이미지가 업로드되면 분석 시작
    if uploaded_image:
        st.markdown("---")
        st.markdown("## 🔍 분석 중...")
        
        with st.spinner("AI가 농작물을 분석하고 있습니다..."):
            # 이미지를 base64로 변환
            image_base64 = load_image_as_base64(uploaded_image)
            
            # AI 분석
            result = analyze_crop_with_ai(image_base64, api_key)
            
            # PIL Image로 변환 (표시용)
            pil_image = Image.open(io.BytesIO(uploaded_image))
        
        # 결과 표시
        st.success("✅ 분석 완료!")
        display_result(result, pil_image)
        
        # 다시 분석하기 버튼
        st.markdown("---")
        if st.button("🔄 다른 이미지 분석하기", width="stretch"):
            st.rerun()
    
    else:
        # 샘플 이미지 안내
        st.info("👆 위에서 이미지를 업로드하거나 촬영해주세요!")
        
        # 예시 결과 미리보기
        with st.expander("📱 결과 예시 보기"):
            st.markdown("""
            ### 🌱 사과
            *Apple*
            
            **분류:** 과일
            
            ---
            
            **🗺️ 유명 생산지**
            - 대구 (대구 사과)
            - 충주 (충주 사과)
            - 예산
            
            **📅 제철**
            9월~11월
            
            **💊 영양 정보**
            비타민C, 식이섬유가 풍부하며 칼륨 함량이 높습니다.
            
            **🏪 보관 방법**
            냉장 보관, 비닐봉지에 넣어 수분 유지
            
            **👅 맛 특징**
            달콤하고 아삭한 식감
            """)


if __name__ == '__main__':
    main()

