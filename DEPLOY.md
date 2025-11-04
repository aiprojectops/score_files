# 🚀 Streamlit Cloud 배포 가이드

이 문서는 농작물 AI 식별 웹앱을 Streamlit Cloud에 배포하는 방법을 설명합니다.

## 📋 사전 준비

### 1. GitHub 계정 필요
- [GitHub](https://github.com) 가입

### 2. Streamlit Cloud 계정 필요
- [Streamlit Cloud](https://streamlit.io/cloud) 접속
- GitHub 계정으로 로그인

---

## 🔧 배포 준비

### 1단계: GitHub에 코드 업로드

#### 방법 A: GitHub Desktop 사용 (추천)
```bash
1. GitHub Desktop 설치
2. New Repository 생성
   - Name: crop-identifier
   - Description: 농작물 AI 식별기
3. Publish repository 클릭
```

#### 방법 B: Git 명령어 사용
```bash
# 프로젝트 폴더에서
git init
git add .
git commit -m "Initial commit: 농작물 AI 식별 웹앱"

# GitHub에 새 repository 생성 후
git remote add origin https://github.com/your-username/crop-identifier.git
git push -u origin main
```

### ⚠️ 중요: .env 파일 제외
`.gitignore` 파일이 이미 `.env`를 제외하도록 설정되어 있습니다.
**절대 API 키를 GitHub에 올리지 마세요!**

---

## 🌐 Streamlit Cloud 배포

### 2단계: Streamlit Cloud에서 배포

1. **[Streamlit Cloud](https://share.streamlit.io/) 접속**

2. **"New app" 버튼 클릭**

3. **Repository 연결**
   ```
   Repository: your-username/crop-identifier
   Branch: main
   Main file path: app.py
   ```

4. **"Deploy!" 버튼 클릭**

5. **Secrets 설정 (중요!)**
   - 배포 중 "Advanced settings" 클릭
   - 또는 배포 후 ⚙️ Settings → Secrets 메뉴
   - 다음 내용 입력:
   ```toml
   OPENAI_API_KEY = "sk-proj-your-actual-api-key-here"
   ```

6. **배포 완료!**
   - URL이 생성됩니다: `https://your-app-name.streamlit.app`
   - 전 세계 어디서나 접속 가능!

---

## 📱 배포 후 사용

### URL 공유
```
https://your-app-name.streamlit.app
```
이 주소를 누구에게나 공유 가능합니다!

### 모바일 접속
- 스마트폰 브라우저에서 URL 접속
- 홈 화면에 추가 가능
- 카메라로 직접 촬영 가능!

---

## 🔄 업데이트 방법

코드를 수정하고 싶을 때:

```bash
# 코드 수정 후
git add .
git commit -m "기능 개선"
git push
```

→ **자동으로 재배포됩니다!** (약 1~2분 소요)

---

## ⚙️ 배포 설정 (선택사항)

### 커스텀 도메인 설정
Streamlit Cloud Pro 플랜 (유료)에서 가능:
- `your-domain.com`으로 연결 가능

### 리소스 제한
- **무료 플랜**:
  - CPU: 1 core
  - RAM: 800MB
  - 동시 접속: 제한 없음
  - 앱 개수: 3개까지

- **충분합니다!** 이 앱은 가벼워서 무료 플랜으로 충분히 작동합니다.

---

## 🐛 문제 해결

### 문제 1: 배포 실패
```
Error: Could not find requirements.txt
```
→ requirements.txt 파일이 프로젝트 루트에 있는지 확인

### 문제 2: API 키 오류
```
Error: OPENAI_API_KEY not found
```
→ Streamlit Cloud의 Secrets에 API 키를 정확히 입력했는지 확인

### 문제 3: 메모리 초과
```
MemoryError
```
→ 이미지 크기 제한 추가 필요 (보통 발생하지 않음)

---

## 💰 비용

### Streamlit Cloud
- ✅ **무료 플랜**: 완전 무료!
- ✅ 3개 앱까지 배포 가능
- ✅ 프라이빗 repository도 가능

### OpenAI API
- 💵 사용량에 따라 과금
- GPT-4o-mini는 매우 저렴:
  - 이미지 1개 분석: 약 $0.01~0.02
  - 월 100회 사용: 약 $1~2
  
---

## 📊 예상 URL

배포하면 이런 형태의 URL이 생성됩니다:

```
https://crop-identifier-abc123.streamlit.app
```

또는 커스텀:
```
https://my-crop-ai.streamlit.app
```

---

## 🎯 배포 체크리스트

배포 전 확인사항:

- [ ] GitHub repository 생성
- [ ] .env 파일이 .gitignore에 포함되어 있는지 확인
- [ ] requirements.txt 파일 확인
- [ ] 코드를 GitHub에 push
- [ ] Streamlit Cloud에 로그인
- [ ] New app 생성
- [ ] Secrets에 OPENAI_API_KEY 입력
- [ ] 배포 완료 확인
- [ ] URL로 접속 테스트

---

## 🌟 배포 성공!

축하합니다! 이제 여러분의 농작물 AI 식별기가 온라인에 있습니다!

URL을 친구들에게 공유하고 사용해보세요! 📱✨

---

## 📚 참고 자료

- [Streamlit Cloud 공식 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [Secrets 관리 가이드](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

