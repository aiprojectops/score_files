# 🌾 농작물 이미지 분류 시스템

OpenAI Vision API를 활용하여 농작물 이미지를 자동으로 분류하고 정확도를 평가하는 시스템입니다.

## 📁 프로젝트 구조

```
project-root/
  ├─ img/                          # 분류할 농작물 이미지들
  │   ├─ img_1.jpg
  │   ├─ img_2.jpg
  │   └─ ...
  ├─ data/
  │   ├─ answer.csv                # 정답 라벨 (템플릿 자동 생성 → 사용자 입력)
  │   └─ predictions.csv           # 예측 결과 (자동 생성)
  ├─ src/
  │   ├─ utils.py                  # 공통 함수 모음
  │   ├─ create_answer_template.py # 정답 템플릿 자동 생성 ⭐ NEW!
  │   ├─ classify_images.py        # 이미지 분류 스크립트
  │   └─ evaluate_accuracy.py      # 정확도 평가 스크립트
  ├─ run_all.py                    # 전체 프로세스 자동 실행 ⭐ NEW!
  ├─ .env                          # API 키 설정 (gitignore)
  ├─ .env.example                  # API 키 설정 예시
  ├─ requirements.txt              # 필수 패키지 목록
  └─ README.md                     # 이 파일
```

## 🚀 사용 방법

### 빠른 시작 (추천!)

```bash
# 1. 필수 패키지 설치
pip install -r requirements.txt

# 2. API 키 설정
cp .env.example .env
# .env 파일을 열어서 본인의 OpenAI API 키를 입력하세요

# 3. 전체 프로세스 자동 실행
python run_all.py
```

---

### 단계별 실행 (상세)

#### 1단계: 환경 설정

```bash
# 필수 패키지 설치
pip install -r requirements.txt

# API 키 설정
cp .env.example .env
# .env 파일을 열어서 본인의 OpenAI API 키를 입력하세요
```

#### 2단계: 정답 템플릿 생성 (자동!)

```bash
python src/create_answer_template.py
```

이 명령어는 `img/` 폴더의 모든 이미지 파일명을 자동으로 읽어서 `data/answer.csv` 파일을 생성합니다!

생성된 파일 예시:
```csv
filename,label
img_1.jpg,
img_2.jpg,
img_3.jpg,
```

#### 3단계: 정답 입력 (수동)

`data/answer.csv` 파일을 열어서 각 이미지를 확인하고 **한글로** 정답을 입력하세요:

```csv
filename,label
img_1.jpg,사과
img_2.jpg,딸기
img_3.jpg,고추
```

💡 **중요**: 파일명에는 정답이 없으므로, 각 이미지를 직접 확인하고 입력해야 합니다.

#### 4단계: 이미지 분류 실행

```bash
python src/classify_images.py
```

실행 결과:
```
[1/6] img_1.jpg -> 예측: 사과 (95.0%), 정답: 사과 ✅
[2/6] img_2.jpg -> 예측: 라즈베리 (62.0%), 정답: 딸기 ❌
...
✅ 완료! 결과가 저장되었습니다: data/predictions.csv
```

#### 5단계: 정확도 평가

```bash
python src/evaluate_accuracy.py
```

실행 결과:
```
📊 전체 정확도
==================
  총 이미지 수      :     6장
  정답 개수         :     5장
  오답 개수         :     1장
  
  🎯 정확도         :  83.3%

🌱 농작물별 정확도
==================
  📌 사과
     - 개수         : 2장
     - 정답         : 2장
     - 정확도       : 100.0%
     - 평균 확신도  : 92.5%
  ...
```

## 🔑 핵심 기능

### 1. 파일명 무시
- API가 파일명이 아닌 **오직 이미지 내용만** 보고 판단하도록 설계
- 명확한 프롬프트로 편향 방지

### 2. 확신도 측정
- 각 예측에 대해 0~1 사이의 확신도 제공
- 모델이 얼마나 확실하게 판단했는지 확인 가능

### 3. 상세한 분석
- 전체 정확도
- 농작물별 정확도
- 오분류 상세 내역
- 평균 확신도

## 📝 주의사항

1. **API 사용료**: OpenAI Vision API는 유료 서비스입니다. 요금제를 확인하세요.
2. **라벨 일관성**: labels.csv의 라벨명을 일관되게 작성하세요 (예: "apple" vs "Apple").
3. **이미지 품질**: 선명하고 농작물이 명확하게 보이는 이미지를 사용하세요.

## 🛠️ 문제 해결

### API 키 오류
```
❌ 오류: OPENAI_API_KEY가 설정되지 않았습니다.
```
→ `.env` 파일에 API 키를 올바르게 입력했는지 확인하세요.

### 정답 파일 없음
```
❌ 정답 파일을 찾을 수 없습니다
```
→ `python src/create_answer_template.py`를 먼저 실행하여 템플릿을 생성하세요.

### 정답 파일 관련
- `create_answer_template.py`를 먼저 실행하세요 (자동으로 answer.csv 생성)
- answer.csv에 **한글**로 정답을 작성하세요 (예: "사과", "딸기", "토마토")
- API도 한글로 답변합니다
- 영어로 작성하면 비교가 안 되니 주의하세요!

### JSON 파싱 오류
```
⚠️ JSON 파싱 실패
```
→ API 응답이 JSON 형식이 아닙니다. 드물게 발생할 수 있으며, 재실행하면 보통 해결됩니다.

## ✨ 새로운 기능 (v2.0)

- ✅ **자동 템플릿 생성**: img 폴더를 스캔하여 answer.csv 자동 생성
- ✅ **통합 실행 스크립트**: run_all.py로 전체 프로세스 한 번에 실행
- ✅ **재사용 가능**: 이미지만 바꾸면 언제든 재사용 가능
- ✅ **Excel 호환**: UTF-8 BOM으로 저장하여 한글 깨짐 없음
- ✅ **한글 지원**: 모든 농작물명을 한글로 입력/출력

## 📚 확장 가능성

- [ ] 여러 모델 비교 (gpt-4o vs gpt-4o-mini)
- [ ] 배치 처리로 속도 향상
- [ ] 웹 인터페이스 추가
- [ ] 혼동 행렬(Confusion Matrix) 시각화
- [ ] 자동 정답 추천 기능

## 🌐 웹앱 버전

실시간으로 농작물을 식별하고 상세 정보를 제공하는 웹앱 버전도 제공됩니다!

### 실행 방법

```bash
streamlit run app.py
```

자세한 내용은 [README_WEBAPP.md](README_WEBAPP.md)를 참고하세요.

### 웹앱 주요 기능
- 📸 이미지 업로드 또는 카메라 촬영
- 🤖 실시간 AI 분석
- 📊 상세 정보 제공 (생산지, 제철, 영양 정보 등)
- 📱 스마트폰에서도 사용 가능

### 🚀 온라인 배포
Streamlit Cloud로 무료 배포 가능! 자세한 내용은 [DEPLOY.md](DEPLOY.md)를 참고하세요.

---

## 📄 라이선스

이 프로젝트는 교육 목적으로 자유롭게 사용 가능합니다.

