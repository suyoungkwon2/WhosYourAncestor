# 🚀 Google Colab 크롤링 가이드

## 📋 준비사항

### 1. Google Colab Pro 구독
- **GPU 가속**: T4 또는 V100 GPU 사용 가능
- **더 긴 실행 시간**: 12시간까지 실행 가능
- **더 많은 메모리**: 32GB RAM 사용 가능

### 2. 필요한 파일
- `colab_crawler.py`: 메인 크롤링 스크립트
- `colab_quick_start.py`: 빠른 테스트용 스크립트
- `requirements.txt`: 필요한 패키지 목록

## 🎯 사용 방법

### 방법 1: 빠른 테스트 (권장)

1. **Google Colab 새 노트북 생성**
2. **다음 코드를 첫 번째 셀에 입력:**

```python
# 파일 업로드
from google.colab import files
print("📁 colab_quick_start.py 파일을 업로드해주세요:")
uploaded = files.upload()

# 실행
!python colab_quick_start.py
```

3. **파일 업로드 후 실행**

### 방법 2: 전체 수집

1. **Google Colab 새 노트북 생성**
2. **다음 코드를 순서대로 실행:**

```python
# 1. 환경 설정
!pip install selenium pillow requests
!apt-get update
!apt-get install -y chromium-chromedriver

# 2. 파일 업로드
from google.colab import files
print("📁 colab_crawler.py 파일을 업로드해주세요:")
uploaded = files.upload()

# 3. 크롤러 실행
!python colab_crawler.py
```

## 📊 예상 결과

### 테스트 실행 시
- **2개 카테고리**: 일본 여성/남성, 한국 여성/남성
- **각 카테고리당 10장**: 총 40장
- **소요 시간**: 약 10-15분

### 전체 실행 시
- **80개 국가 × 2개 성별**: 160개 카테고리
- **각 카테고리당 100장**: 총 16,000장
- **소요 시간**: 약 4-5시간

## 🛠️ 문제 해결

### 1. Chrome 드라이버 오류
```python
# 드라이버 재설치
!apt-get remove chromium-chromedriver
!apt-get install -y chromium-chromedriver
```

### 2. 메모리 부족
```python
# 메모리 정리
import gc
gc.collect()
```

### 3. 실행 시간 초과
- **Colab Pro 사용**: 12시간 실행 가능
- **단계별 실행**: 국가별로 나누어 실행

## 📁 결과 다운로드

### 수집된 데이터 확인
```python
import os

dataset_path = "/content/dataset"
if os.path.exists(dataset_path):
    print("📊 수집된 데이터:")
    for root, dirs, files in os.walk(dataset_path):
        if files:
            print(f"  {root}: {len(files)}개 파일")
```

### 데이터 압축 및 다운로드
```python
# 압축
!cd /content && zip -r dataset.zip dataset/

# 다운로드
from google.colab import files
files.download('/content/dataset.zip')
```

## ⚠️ 주의사항

### 1. 실행 시간
- **테스트**: 10-15분
- **전체 수집**: 4-5시간
- **Colab 무료 버전**: 12시간 제한

### 2. 네트워크 제한
- **Google 검색 제한**: 과도한 요청 시 차단 가능
- **해결책**: 요청 간격 조절 (0.5초)

### 3. 저장 공간
- **16,000장 × 50KB**: 약 800MB
- **Colab 용량**: 충분히 사용 가능

## 🎯 최적화 팁

### 1. 배치 실행
```python
# 국가별로 나누어 실행
countries_batch1 = ["japanese", "korean", "chinese"]
countries_batch2 = ["british", "german", "french"]
# ...
```

### 2. 병렬 처리
```python
# 여러 노트북에서 동시 실행
# 노트북 1: 1-20번 국가
# 노트북 2: 21-40번 국가
# ...
```

### 3. 중간 저장
```python
# 진행 상황 저장
import json
progress = {"completed": ["japanese", "korean"], "remaining": ["chinese", "british"]}
with open("/content/progress.json", "w") as f:
    json.dump(progress, f)
```

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. **Colab Pro 구독 여부**
2. **GPU 가속 활성화**
3. **파일 업로드 완료**
4. **인터넷 연결 상태**

---

**🚀 이제 Colab에서 크롤링을 시작해보세요!** 