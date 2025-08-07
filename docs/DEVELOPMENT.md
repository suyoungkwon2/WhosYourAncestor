# 🚀 개발 워크플로우 가이드

## 🌐 프로젝트 정보

### **📁 저장소**
- **GitHub**: https://github.com/suyoungkwon2/WhosYourAncestor
- **Vercel**: https://vercel.com/su-young-kwons-projects/whos-your-ancestor

### **🚀 배포 URL**
- **프로덕션**: https://whos-your-ancestor-kjs9ckaai-su-young-kwons-projects.vercel.app
- **도메인**: jamyeah.com (연결 예정)

## 🌿 브랜치 전략

### **Main 브랜치 (Production)**
- **목적**: 프로덕션 배포용
- **배포**: jamyeah.com (프로덕션 도메인)
- **보호**: Pull Request 필수, 자동 테스트 통과 필수

### **Dev 브랜치 (Development)**
- **목적**: 개발 및 테스트용
- **배포**: Vercel 프리뷰 URL
- **특징**: 자유로운 개발, 실험적 기능 테스트

## 🔄 개발 프로세스

### **1. 기능 개발**
```bash
# dev 브랜치에서 개발
git checkout dev
git pull origin dev

# 새 기능 브랜치 생성 (선택사항)
git checkout -b feature/tensorflow-integration

# 개발 완료 후
git add .
git commit -m "feat: Add TensorFlow.js integration"
git push origin dev
```

### **2. Pull Request 생성**
1. **GitHub**에서 **"Compare & pull request"** 클릭
2. **dev → main** 방향으로 PR 생성
3. **코드 리뷰** 및 **테스트 통과** 확인
4. **Merge** 후 자동 배포

### **3. 배포 확인**
- **dev 브랜치**: Vercel 프리뷰 URL
- **main 브랜치**: jamyeah.com (프로덕션)

## 🛠️ 개발 환경 설정

### **로컬 개발**
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드 테스트
npm run build

# 린팅
npm run lint
```

### **환경 변수**
- **개발**: `.env.local` (Git에 포함되지 않음)
- **프로덕션**: Vercel 대시보드에서 설정

### **브라우저 접속**
- **로컬 개발**: http://localhost:5173
- **프로덕션**: https://whos-your-ancestor-kjs9ckaai-su-young-kwons-projects.vercel.app

## 📋 현재 진행 상황

### **✅ 완료된 작업**
- [x] React + Vite 프로젝트 설정
- [x] Tailwind CSS 스타일링
- [x] GitHub 저장소 연결 (https://github.com/suyoungkwon2/WhosYourAncestor)
- [x] Vercel 자동 배포 설정 (https://vercel.com/su-young-kwons-projects/whos-your-ancestor)
- [x] 브랜치 전략 설정 (main/dev)
- [x] CI/CD 파이프라인 구축
- [x] 개발 워크플로우 문서화

### **🔄 진행 중인 작업**
- [ ] TensorFlow.js 얼굴 인식 기능
- [ ] 다국어 지원 (한/영/일/중)
- [ ] 얼굴 업로드 UI
- [ ] 결과 시각화
- [ ] jamyeah.com 도메인 연결

### **📅 예정된 작업**
- [ ] Google Analytics 연동
- [ ] 성능 최적화
- [ ] SEO 설정
- [ ] 애드센스 준비

## 🚨 주의사항

1. **main 브랜치 직접 푸시 금지**
2. **Pull Request 필수**
3. **테스트 통과 후 머지**
4. **커밋 메시지 규칙 준수**

## 📞 문제 해결

- **배포 문제**: Vercel 대시보드 확인
- **빌드 오류**: 로컬에서 `npm run build` 테스트
- **환경 변수**: Vercel 대시보드에서 설정 