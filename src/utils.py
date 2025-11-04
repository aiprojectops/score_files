"""
농작물 이미지 분류를 위한 유틸리티 함수 모음

이 모듈은 다음 기능을 제공합니다:
- 이미지 파일을 base64로 변환
- OpenAI Vision API 호출
- 정답 라벨 파일 로드
"""

import base64
import json
import csv
from pathlib import Path
from typing import Dict, Optional
import openai


# 상수 정의: 매직 넘버/문자열 방지
SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
BASE64_IMAGE_PREFIX = 'data:image/jpeg;base64,'
VISION_MODEL_NAME = 'gpt-4o-mini'
API_MAX_TOKENS = 300


def load_image_as_base64(image_path: str) -> str:
    """
    이미지 파일을 base64 인코딩된 문자열로 변환합니다.
    
    Args:
        image_path: 변환할 이미지 파일의 경로
        
    Returns:
        base64로 인코딩된 이미지 문자열 (data URI 형식)
        
    Raises:
        FileNotFoundError: 이미지 파일이 존재하지 않는 경우
    """
    image_file_path = Path(image_path)
    
    if not image_file_path.exists():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
    
    with open(image_file_path, 'rb') as image_file:
        image_binary_data = image_file.read()
        encoded_image = base64.b64encode(image_binary_data).decode('utf-8')
        
    return f"{BASE64_IMAGE_PREFIX}{encoded_image}"


def call_vision_api(
    image_base64: str,
    api_key: str
) -> Optional[Dict[str, any]]:
    """
    OpenAI Vision API를 호출하여 이미지 속 농작물을 분류합니다.
    
    이 함수는 파일명이 아닌 오직 이미지 내용만으로 판단하도록
    명확한 프롬프트를 사용합니다.
    
    Args:
        image_base64: base64 인코딩된 이미지 문자열
        api_key: OpenAI API 키
        
    Returns:
        {"crop": "apple", "confidence": 0.93} 형식의 딕셔너리
        오류 발생 시 None 반환
    """
    # API 클라이언트 설정
    client = openai.OpenAI(api_key=api_key)
    
    # 시스템 프롬프트: 모델의 역할과 출력 형식 지정 (한글 지원)
    system_prompt = """당신은 농작물 이미지 분류 전문가입니다.
절대로 파일명을 보지 말고, 오직 이미지 내용만 보고 판단하세요.
반드시 다음과 같은 JSON 형식으로만 답변하세요:
{"crop": "사과", "confidence": 0.93}

규칙:
- "crop": 농작물의 한글 이름 (예: "사과", "딸기", "토마토", "고추", "포도")
- "confidence": 0.0에서 1.0 사이의 소수점 숫자
- 추가 설명이나 마크다운 형식 없이 JSON만 반환하세요
- 반드시 JSON 객체만 반환하세요"""

    # 사용자 프롬프트: 구체적인 요청 (한글)
    user_prompt = """이 이미지를 보고 어떤 농작물인지 식별하세요.
농작물 이름(한글)과 확신도를 포함한 JSON 객체만 반환하세요."""

    try:
        response = client.chat.completions.create(
            model=VISION_MODEL_NAME,
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
            max_tokens=API_MAX_TOKENS
        )
        
        # 응답 텍스트 추출
        response_text = response.choices[0].message.content.strip()
        
        # JSON 파싱 시도
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            print(f"⚠️  JSON 파싱 실패. 응답: {response_text}")
            return None
            
    except Exception as api_error:
        print(f"❌ API 호출 중 오류 발생: {str(api_error)}")
        return None


def load_answers_from_csv(csv_path: str) -> Dict[str, str]:
    """
    answer.csv 파일에서 정답 라벨을 읽어 딕셔너리로 반환합니다.
    
    여러 인코딩을 자동으로 시도하여 Windows 환경에서도 안전하게 작동합니다.
    
    Args:
        csv_path: answer.csv 파일의 경로
        
    Returns:
        {파일명: 정답라벨} 형태의 딕셔너리
        예: {"img_1.jpg": "사과", "img_2.jpg": "딸기"}
        
    Raises:
        FileNotFoundError: CSV 파일이 존재하지 않는 경우
    """
    csv_file_path = Path(csv_path)
    
    if not csv_file_path.exists():
        raise FileNotFoundError(f"라벨 파일을 찾을 수 없습니다: {csv_path}")
    
    labels_dict = {}
    
    # Windows에서 흔히 사용되는 인코딩들을 순서대로 시도
    encodings_to_try = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']
    successful_encoding = None
    
    for encoding in encodings_to_try:
        try:
            with open(csv_file_path, 'r', encoding=encoding, newline='') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                
                # 데이터 읽기 시도
                for row in csv_reader:
                    filename = row['filename'].strip()
                    label = row['label'].strip()
                    
                    # 빈 라벨 체크
                    if not label:
                        print(f"⚠️  경고: {filename}의 라벨이 비어있습니다. 수동으로 입력해주세요.")
                        continue
                        
                    labels_dict[filename] = label
                
                successful_encoding = encoding
                break
                
        except (UnicodeDecodeError, UnicodeError, KeyError):
            # 이 인코딩으로 실패하면 다음 시도
            labels_dict = {}
            continue
    
    if not labels_dict:
        raise ValueError(
            f"파일을 읽을 수 없습니다. {csv_path}의 형식을 확인해주세요."
        )
    
    # 성공한 인코딩 정보 출력
    if successful_encoding and successful_encoding != 'utf-8':
        print(f"ℹ️  {csv_path}를 {successful_encoding} 인코딩으로 읽었습니다.")
    
    return labels_dict


def validate_image_file(file_path: Path) -> bool:
    """
    파일이 유효한 이미지 파일인지 확인합니다.
    
    Args:
        file_path: 검증할 파일의 Path 객체
        
    Returns:
        유효한 이미지 파일이면 True, 아니면 False
    """
    if not file_path.is_file():
        return False
    
    return file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS

