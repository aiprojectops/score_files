"""
농작물 이미지 분류 프로젝트 전체 실행 스크립트

이 스크립트는 다음 순서로 모든 과정을 자동으로 실행합니다:
1. answer.csv 템플릿 생성 (이미 있으면 스킵 가능)
2. 사용자가 정답 입력 (수동 단계)
3. 이미지 분류 실행
4. 정확도 평가
"""

import sys
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
ANSWER_FILE_PATH = PROJECT_ROOT / 'data' / 'answer.csv'


def run_script(script_path: str, description: str) -> bool:
    """
    파이썬 스크립트를 실행합니다.
    
    Args:
        script_path: 실행할 스크립트 경로
        description: 스크립트 설명
        
    Returns:
        성공 여부
    """
    print()
    print("=" * 70)
    print(f"▶ {description}")
    print("=" * 70)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError:
        print()
        print(f"❌ {description} 실행 중 오류가 발생했습니다.")
        return False


def check_answer_file_filled() -> bool:
    """
    answer.csv 파일이 존재하고 정답이 입력되었는지 확인합니다.
    
    Returns:
        정답이 입력되었으면 True
    """
    if not ANSWER_FILE_PATH.exists():
        return False
    
    # 파일 내용 확인
    try:
        with open(ANSWER_FILE_PATH, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            # 헤더 제외하고 최소 1줄은 있어야 하고, 빈 라벨이 없어야 함
            if len(lines) < 2:
                return False
            
            # 두 번째 줄부터 확인 (헤더 제외)
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) < 2 or not parts[1]:  # label이 비어있으면
                    return False
            
            return True
    except Exception:
        return False


def main():
    """
    메인 실행 함수
    """
    print()
    print("*" * 70)
    print("🌾 농작물 이미지 분류 시스템 - 전체 실행")
    print("*" * 70)
    
    # 1단계: answer.csv 템플릿 생성
    if not ANSWER_FILE_PATH.exists():
        print()
        print("📋 1단계: 정답 템플릿 생성")
        if not run_script('src/create_answer_template.py', '정답 템플릿 생성'):
            return
        
        print()
        print("=" * 70)
        print("⏸️  잠깐! 다음 단계를 진행하기 전에:")
        print("=" * 70)
        print()
        print("  1. data/answer.csv 파일을 여세요")
        print("  2. 각 이미지를 확인하고 정답을 입력하세요")
        print("  3. 저장 후 이 스크립트를 다시 실행하세요")
        print()
        print("=" * 70)
        return
    
    # 정답이 입력되었는지 확인
    if not check_answer_file_filled():
        print()
        print("=" * 70)
        print("⚠️  경고: answer.csv 파일에 정답이 입력되지 않았습니다")
        print("=" * 70)
        print()
        print("  📁 파일 위치: data/answer.csv")
        print()
        print("  각 이미지를 확인하고 label 컬럼에 정답을 입력한 후")
        print("  저장하고 다시 실행해주세요.")
        print()
        print("=" * 70)
        return
    
    # 2단계: 이미지 분류
    print()
    print("🔍 2단계: 이미지 분류 실행")
    if not run_script('src/classify_images.py', 'AI 이미지 분류'):
        return
    
    # 3단계: 정확도 평가
    print()
    print("📊 3단계: 정확도 평가")
    if not run_script('src/evaluate_accuracy.py', '정확도 평가'):
        return
    
    # 완료
    print()
    print("*" * 70)
    print("🎉 모든 과정이 완료되었습니다!")
    print("*" * 70)
    print()
    print("📊 결과 파일:")
    print(f"  - 정답: data/answer.csv")
    print(f"  - 예측: data/predictions.csv")
    print()
    print("*" * 70)
    print()


if __name__ == '__main__':
    main()

