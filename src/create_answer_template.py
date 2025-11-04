"""
정답 템플릿 파일 생성 스크립트

img/ 폴더의 모든 이미지 파일명을 읽어서
answer.csv 파일을 자동으로 생성합니다.
사용자는 생성된 파일에 정답만 입력하면 됩니다.
"""

import csv
from pathlib import Path
from typing import List


# 경로 상수
PROJECT_ROOT = Path(__file__).parent.parent
IMAGE_FOLDER_PATH = PROJECT_ROOT / 'img'
ANSWER_FILE_PATH = PROJECT_ROOT / 'data' / 'answer.csv'
SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')


def get_all_image_files(folder_path: Path) -> List[Path]:
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
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    
    # 파일명 기준으로 정렬
    return sorted(image_files, key=lambda x: x.name)


def create_answer_template(image_files: List[Path], output_path: Path) -> None:
    """
    이미지 파일 목록을 기반으로 answer.csv 템플릿을 생성합니다.
    
    Args:
        image_files: 이미지 파일 Path 객체의 리스트
        output_path: 저장할 CSV 파일 경로
    """
    # data 폴더가 없으면 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # UTF-8 BOM으로 저장 (Excel에서도 제대로 보임)
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
        fieldnames = ['filename', 'label']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # 헤더 작성
        writer.writeheader()
        
        # 각 이미지 파일명 작성 (label은 비워둠)
        for image_file in image_files:
            writer.writerow({
                'filename': image_file.name,
                'label': ''
            })


def display_next_steps(answer_file_path: Path, image_count: int) -> None:
    """
    다음 단계 안내를 출력합니다.
    
    Args:
        answer_file_path: 생성된 answer.csv 파일 경로
        image_count: 처리된 이미지 개수
    """
    print()
    print("=" * 70)
    print("[3/3] answer.csv 파일이 생성되었습니다!")
    print("=" * 70)
    print()
    print(f"[FILE] 위치: {answer_file_path}")
    print(f"[COUNT] 이미지 개수: {image_count}개")
    print()
    print("-" * 70)
    print("다음 단계:")
    print("-" * 70)
    print()
    print("1. data/answer.csv 파일을 여세요")
    print()
    print("2. 각 이미지를 확인하고 'label' 컬럼에 정답을 입력하세요")
    print("   예시:")
    print("   filename      | label")
    print("   ------------- | --------")
    print("   img_1.jpg     | 사과")
    print("   img_2.jpg     | 딸기")
    print("   img_3.jpg     | 토마토")
    print()
    print("3. 저장 후, 아래 명령어를 실행하세요:")
    print("   python src/classify_images.py")
    print()
    print("-" * 70)
    print("[TIP] Excel이나 메모장에서 편집 가능합니다!")
    print("=" * 70)
    print()


def main():
    """
    메인 실행 함수: 이미지 파일을 스캔하고 answer.csv를 생성합니다.
    """
    print()
    print("=" * 70)
    print("[1/3] 정답 템플릿 생성")
    print("=" * 70)
    print()
    
    # 1. 이미지 파일 목록 가져오기
    print(f"이미지 폴더 스캔 중: {IMAGE_FOLDER_PATH}")
    image_files = get_all_image_files(IMAGE_FOLDER_PATH)
    
    if not image_files:
        print()
        print("[ERROR] 이미지 파일을 찾을 수 없습니다.")
        print(f"[TIP] {IMAGE_FOLDER_PATH} 폴더에 이미지를 추가해주세요.")
        return
    
    print(f"[OK] {len(image_files)}개의 이미지 파일을 발견했습니다:")
    print()
    for idx, img_file in enumerate(image_files, start=1):
        print(f"   {idx}. {img_file.name}")
    print()
    
    # 2. 기존 answer.csv 파일 확인
    if ANSWER_FILE_PATH.exists():
        print(f"[WARNING] {ANSWER_FILE_PATH} 파일이 이미 존재합니다.")
        print()
        
        # 사용자에게 덮어쓰기 여부 확인 (자동 승인)
        print("   기존 파일을 덮어쓰고 새로 생성합니다.")
        print()
    
    # 3. answer.csv 생성
    print("[2/3] answer.csv 파일 생성 중...")
    create_answer_template(image_files, ANSWER_FILE_PATH)
    
    # 4. 다음 단계 안내
    display_next_steps(ANSWER_FILE_PATH, len(image_files))


if __name__ == '__main__':
    main()

