"""
농작물 이미지 분류 정확도 평가 스크립트

predictions.csv 파일을 읽어서 정확도를 계산하고,
농작물별 통계를 출력합니다.
"""

import csv
from pathlib import Path
from typing import List, Dict
from collections import defaultdict


# 경로 상수
PROJECT_ROOT = Path(__file__).parent.parent
PREDICTIONS_FILE_PATH = PROJECT_ROOT / 'data' / 'predictions.csv'


def load_predictions_from_csv(csv_path: Path) -> List[Dict]:
    """
    predictions.csv 파일에서 예측 결과를 읽어옵니다.
    
    여러 인코딩을 자동으로 시도하여 Windows 환경에서도 안전하게 작동합니다.
    
    Args:
        csv_path: predictions.csv 파일 경로
        
    Returns:
        예측 결과 딕셔너리의 리스트
        
    Raises:
        FileNotFoundError: CSV 파일이 존재하지 않는 경우
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"예측 결과 파일을 찾을 수 없습니다: {csv_path}")
    
    predictions = []
    
    # Windows에서 흔히 사용되는 인코딩들을 순서대로 시도
    encodings_to_try = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']
    
    for encoding in encodings_to_try:
        try:
            with open(csv_path, 'r', encoding=encoding, newline='') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                
                for row in csv_reader:
                    # ERROR 레이블은 제외
                    if row['pred_label'] == 'ERROR':
                        continue
                        
                    predictions.append({
                        'filename': row['filename'],
                        'true_label': row['true_label'],
                        'pred_label': row['pred_label'],
                        'pred_confidence': float(row['pred_confidence'])
                    })
                
                # 성공하면 루프 종료
                break
                
        except (UnicodeDecodeError, UnicodeError, KeyError):
            # 이 인코딩으로 실패하면 다음 시도
            predictions = []
            continue
    
    if not predictions:
        raise ValueError(
            f"파일을 읽을 수 없습니다. {csv_path}의 형식을 확인해주세요."
        )
    
    return predictions


def calculate_overall_accuracy(predictions: List[Dict]) -> Dict[str, any]:
    """
    전체 정확도를 계산합니다.
    
    Args:
        predictions: 예측 결과 리스트
        
    Returns:
        {'total': 총개수, 'correct': 정답개수, 'accuracy': 정확도} 딕셔너리
    """
    if not predictions:
        return {'total': 0, 'correct': 0, 'accuracy': 0.0}
    
    total_count = len(predictions)
    correct_count = 0
    
    for prediction in predictions:
        # 대소문자 구분 없이 비교
        if prediction['true_label'].lower() == prediction['pred_label'].lower():
            correct_count += 1
    
    accuracy = (correct_count / total_count) * 100
    
    return {
        'total': total_count,
        'correct': correct_count,
        'accuracy': accuracy
    }


def calculate_per_crop_statistics(predictions: List[Dict]) -> Dict[str, Dict]:
    """
    농작물별 통계를 계산합니다.
    
    Args:
        predictions: 예측 결과 리스트
        
    Returns:
        {농작물명: {통계정보}} 딕셔너리
    """
    # 농작물별로 데이터 그룹화
    crop_data = defaultdict(lambda: {
        'total': 0,
        'correct': 0,
        'confidence_sum': 0.0
    })
    
    for prediction in predictions:
        true_crop = prediction['true_label']
        pred_crop = prediction['pred_label']
        confidence = prediction['pred_confidence']
        
        crop_data[true_crop]['total'] += 1
        crop_data[true_crop]['confidence_sum'] += confidence
        
        # 정답 여부 확인
        if true_crop.lower() == pred_crop.lower():
            crop_data[true_crop]['correct'] += 1
    
    # 통계 계산
    crop_statistics = {}
    
    for crop_name, data in crop_data.items():
        accuracy = (data['correct'] / data['total']) * 100
        avg_confidence = data['confidence_sum'] / data['total']
        
        crop_statistics[crop_name] = {
            'total': data['total'],
            'correct': data['correct'],
            'accuracy': accuracy,
            'avg_confidence': avg_confidence
        }
    
    return crop_statistics


def find_misclassified_images(predictions: List[Dict]) -> List[Dict]:
    """
    잘못 분류된 이미지들을 찾아 반환합니다.
    
    Args:
        predictions: 예측 결과 리스트
        
    Returns:
        잘못 분류된 이미지 정보 리스트
    """
    misclassified = []
    
    for prediction in predictions:
        if prediction['true_label'].lower() != prediction['pred_label'].lower():
            misclassified.append(prediction)
    
    return misclassified


def display_overall_results(accuracy_info: Dict[str, any]) -> None:
    """
    전체 정확도 결과를 콘솔에 출력합니다.
    
    Args:
        accuracy_info: 정확도 정보 딕셔너리
    """
    print("=" * 70)
    print("📊 전체 정확도")
    print("=" * 70)
    print()
    print(f"  총 이미지 수      : {accuracy_info['total']:>5}장")
    print(f"  정답 개수         : {accuracy_info['correct']:>5}장")
    print(f"  오답 개수         : {accuracy_info['total'] - accuracy_info['correct']:>5}장")
    print()
    print(f"  🎯 정확도         : {accuracy_info['accuracy']:>5.1f}%")
    print()


def display_per_crop_statistics(crop_stats: Dict[str, Dict]) -> None:
    """
    농작물별 통계를 콘솔에 출력합니다.
    
    Args:
        crop_stats: 농작물별 통계 딕셔너리
    """
    print("=" * 70)
    print("🌱 농작물별 정확도")
    print("=" * 70)
    print()
    
    # 정확도 순으로 정렬
    sorted_crops = sorted(
        crop_stats.items(),
        key=lambda x: x[1]['accuracy'],
        reverse=True
    )
    
    for crop_name, stats in sorted_crops:
        print(f"  📌 {crop_name}")
        print(f"     - 개수         : {stats['total']}장")
        print(f"     - 정답         : {stats['correct']}장")
        print(f"     - 정확도       : {stats['accuracy']:.1f}%")
        print(f"     - 평균 확신도  : {stats['avg_confidence']:.1f}%")
        print()


def display_misclassified_images(misclassified: List[Dict]) -> None:
    """
    잘못 분류된 이미지들을 콘솔에 출력합니다.
    
    Args:
        misclassified: 잘못 분류된 이미지 정보 리스트
    """
    if not misclassified:
        print("=" * 70)
        print("🎉 축하합니다! 모든 이미지가 정확하게 분류되었습니다!")
        print("=" * 70)
        return
    
    print("=" * 70)
    print("❌ 오분류 상세 내역")
    print("=" * 70)
    print()
    
    for index, item in enumerate(misclassified, start=1):
        print(f"  {index}. {item['filename']}")
        print(f"     정답 : {item['true_label']}")
        print(f"     예측 : {item['pred_label']} (확신도: {item['pred_confidence']*100:.1f}%)")
        print()


def main():
    """
    메인 실행 함수: 정확도를 계산하고 결과를 출력합니다.
    """
    print()
    print("=" * 70)
    print("🧮 정확도 평가 시작")
    print("=" * 70)
    print()
    
    # 1. 예측 결과 로드
    try:
        predictions = load_predictions_from_csv(PREDICTIONS_FILE_PATH)
    except FileNotFoundError:
        print(f"❌ 예측 결과 파일을 찾을 수 없습니다: {PREDICTIONS_FILE_PATH}")
        print()
        print("💡 먼저 classify_images.py를 실행해주세요:")
        print("   python src/classify_images.py")
        return
    
    if not predictions:
        print("⚠️  분석할 예측 결과가 없습니다.")
        return
    
    # 2. 전체 정확도 계산
    accuracy_info = calculate_overall_accuracy(predictions)
    display_overall_results(accuracy_info)
    
    # 3. 농작물별 통계 계산
    crop_statistics = calculate_per_crop_statistics(predictions)
    display_per_crop_statistics(crop_statistics)
    
    # 4. 잘못 분류된 이미지 분석
    misclassified_images = find_misclassified_images(predictions)
    display_misclassified_images(misclassified_images)
    
    print("=" * 70)
    print("✅ 평가 완료!")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()

