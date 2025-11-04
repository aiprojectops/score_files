"""
농작물 이미지 분류 실행 스크립트

img/ 폴더의 모든 이미지를 OpenAI Vision API로 분류하고,
결과를 data/predictions.csv에 저장합니다.
"""

import csv
import os
import sys
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# 부모 디렉토리를 경로에 추가하여 src 모듈 import 가능하도록
sys.path.append(str(Path(__file__).parent))

from utils import (
    load_image_as_base64,
    call_vision_api,
    load_answers_from_csv,
    validate_image_file
)


# 경로 상수
PROJECT_ROOT = Path(__file__).parent.parent
IMAGE_FOLDER_PATH = PROJECT_ROOT / 'img'
ANSWER_FILE_PATH = PROJECT_ROOT / 'data' / 'answer.csv'
PREDICTIONS_FILE_PATH = PROJECT_ROOT / 'data' / 'predictions.csv'


def get_image_files(folder_path: Path) -> List[Path]:
    """
    지정된 폴더에서 모든 이미지 파일을 찾아 정렬하여 반환합니다.
    
    Args:
        folder_path: 이미지가 들어있는 폴더 경로
        
    Returns:
        이미지 파일 Path 객체의 리스트 (이름순 정렬)
    """
    if not folder_path.exists():
        print(f"❌ 이미지 폴더가 존재하지 않습니다: {folder_path}")
        return []
    
    image_files = [
        file_path for file_path in folder_path.iterdir()
        if validate_image_file(file_path)
    ]
    
    # 파일명 기준으로 정렬
    return sorted(image_files, key=lambda x: x.name)


def classify_single_image(
    image_path: Path,
    api_key: str,
    true_label: str
) -> Dict[str, any]:
    """
    단일 이미지를 분류하고 결과를 반환합니다.
    
    Args:
        image_path: 분류할 이미지 파일 경로
        api_key: OpenAI API 키
        true_label: 정답 라벨
        
    Returns:
        분류 결과 딕셔너리
    """
    try:
        # 이미지를 base64로 변환
        image_base64 = load_image_as_base64(str(image_path))
        
        # Vision API 호출
        prediction_result = call_vision_api(image_base64, api_key)
        
        # API 호출 실패 처리
        if prediction_result is None:
            return {
                'filename': image_path.name,
                'true_label': true_label,
                'pred_label': 'ERROR',
                'pred_confidence': 0.0
            }
        
        # 결과 추출
        predicted_crop = prediction_result.get('crop', 'unknown')
        predicted_confidence = prediction_result.get('confidence', 0.0)
        
        return {
            'filename': image_path.name,
            'true_label': true_label,
            'pred_label': predicted_crop,
            'pred_confidence': predicted_confidence
        }
        
    except Exception as error:
        print(f"❌ {image_path.name} 처리 중 오류: {str(error)}")
        return {
            'filename': image_path.name,
            'true_label': true_label,
            'pred_label': 'ERROR',
            'pred_confidence': 0.0
        }


def save_predictions_to_csv(
    predictions: List[Dict],
    output_path: Path
) -> None:
    """
    예측 결과를 CSV 파일로 저장합니다.
    
    Excel에서도 제대로 보이도록 UTF-8 BOM으로 저장합니다.
    
    Args:
        predictions: 예측 결과 리스트
        output_path: 저장할 CSV 파일 경로
    """
    # data 폴더가 없으면 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # utf-8-sig: Excel에서 한글이 깨지지 않도록 BOM 포함
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
        fieldnames = ['filename', 'true_label', 'pred_label', 'pred_confidence']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(predictions)


def display_progress(
    current_index: int,
    total_count: int,
    filename: str,
    predicted_label: str,
    confidence: float,
    true_label: str
) -> None:
    """
    진행 상황을 콘솔에 표시합니다.
    
    Args:
        current_index: 현재 처리 중인 이미지 번호 (1부터 시작)
        total_count: 전체 이미지 개수
        filename: 파일명
        predicted_label: 예측된 라벨
        confidence: 확신도
        true_label: 정답 라벨
    """
    # 정답 여부 확인
    is_correct = predicted_label.lower() == true_label.lower()
    result_icon = "✅" if is_correct else "❌"
    
    # 확신도를 퍼센트로 변환
    confidence_percent = confidence * 100
    
    print(
        f"[{current_index}/{total_count}] {filename} -> "
        f"예측: {predicted_label} ({confidence_percent:.1f}%), "
        f"정답: {true_label} {result_icon}"
    )


def main():
    """
    메인 실행 함수: 모든 이미지를 분류하고 결과를 저장합니다.
    """
    print("=" * 70)
    print("🌾 농작물 이미지 분류 시스템")
    print("=" * 70)
    print()
    
    # 1. 환경 변수 로드
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ 오류: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("💡 .env 파일에 다음과 같이 추가해주세요:")
        print("   OPENAI_API_KEY=your_api_key_here")
        return
    
    print("✅ API 키 로드 완료")
    
    # 2. 정답 라벨 로드
    try:
        answers_dict = load_answers_from_csv(str(ANSWER_FILE_PATH))
        print(f"✅ 정답 라벨 로드 완료: {len(answers_dict)}개")
    except FileNotFoundError:
        print(f"❌ 정답 파일을 찾을 수 없습니다: {ANSWER_FILE_PATH}")
        print()
        print("💡 먼저 정답 템플릿을 생성해주세요:")
        print("   python src/create_answer_template.py")
        return
    except ValueError:
        print(f"❌ 정답 파일을 읽을 수 없습니다: {ANSWER_FILE_PATH}")
        print("💡 파일 형식을 확인해주세요.")
        return
    
    if not answers_dict:
        print("⚠️  경고: 유효한 라벨이 없습니다. data/answer.csv를 확인해주세요.")
        return
    
    # 3. 이미지 파일 목록 가져오기
    image_files = get_image_files(IMAGE_FOLDER_PATH)
    
    if not image_files:
        print(f"❌ {IMAGE_FOLDER_PATH}에 이미지 파일이 없습니다.")
        return
    
    print(f"✅ 이미지 파일 발견: {len(image_files)}개")
    print()
    print("-" * 70)
    print("🔍 분류 시작...")
    print("-" * 70)
    print()
    
    # 4. 각 이미지 분류
    all_predictions = []
    total_images = len(image_files)
    
    for index, image_path in enumerate(image_files, start=1):
        filename = image_path.name
        
        # 정답 라벨 가져오기
        true_label = answers_dict.get(filename, 'unknown')
        
        # 라벨이 없는 경우 스킵
        if true_label == 'unknown':
            print(f"[{index}/{total_images}] {filename} -> ⚠️  라벨 없음 (스킵)")
            continue
        
        # 이미지 분류
        prediction = classify_single_image(image_path, api_key, true_label)
        all_predictions.append(prediction)
        
        # 진행 상황 표시
        display_progress(
            index,
            total_images,
            filename,
            prediction['pred_label'],
            prediction['pred_confidence'],
            true_label
        )
    
    # 5. 결과 저장
    if all_predictions:
        save_predictions_to_csv(all_predictions, PREDICTIONS_FILE_PATH)
        print()
        print("-" * 70)
        print(f"✅ 완료! 결과가 저장되었습니다: {PREDICTIONS_FILE_PATH}")
        print("-" * 70)
        print()
        print("💡 다음 명령으로 정확도를 확인하세요:")
        print(f"   python src/evaluate_accuracy.py")
    else:
        print()
        print("⚠️  처리된 이미지가 없습니다.")


if __name__ == '__main__':
    main()

