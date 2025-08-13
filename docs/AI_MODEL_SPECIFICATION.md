# AI 모델 기술 사양서 (AI Model Technical Specification)

## 1. 개요

이 문서는 "Who's Your Ancestor" 프로젝트의 핵심 기능인 **얼굴 기반 혈통 분석 AI 모델**의 최종 학습 과정과 기술적 사양을 상세히 기록합니다. 이 문서는 향후 모델 성능 개선, 유지보수 및 인수인계를 위한 기술 참고 자료로 활용됩니다.

- **최종 업데이트**: 2025-08-11
- **최종 모델 버전**: v1.0
- **담당자**: melkwon

---

## 2. 데이터 사양

- **데이터 소스**: 웹 크롤링을 통해 수집된 공개 인물 이미지
- **데이터셋 구성**:
    - **총 클래스(국가) 수**: 12개
    - **클래스 목록**: `british`, `chinese`, `ethiopian`, `french`, `indian`, `indigenous`, `japanese`, `korean`, `mexican`, `nigerian`, `russian`, `saudi`
    - **총 이미지 수**: 약 2,000 ~ 2,200장 (클래스당 약 150 ~ 200장)
- **이미지 전처리**:
    - **입력 크기**: `224x224` 픽셀
    - **채널**: RGB (3채널)
    - **정규화**: 0~1 범위로 픽셀 값 조정 (`/ 255.0`)

---

## 3. 학습 환경

- **플랫폼**: **Kaggle Notebooks** (무료 GPU 세션 활용)
- **주요 라이브러리 및 프레임워크**:
    - **TensorFlow**: v2.18.0
    - **Python**: v3.11
    - **TensorFlow.js**: 웹 모델 변환 및 배포용

---

## 4. 모델 아키텍처

- **베이스 모델**: **`EfficientNetV2B0`**
    - **선정 이유**: `MobileNetV2`보다 더 높은 성능을 보이면서도, 웹 환경에 적합한 가벼운 모델. 복잡하고 미세한 이미지 특징을 학습하는 데 뛰어남.
    - **사전 학습 가중치**: `ImageNet`
- **분류기 헤드 (Classifier Head)**:
    - `GlobalAveragePooling2D`
    - `Dense (256 units, ReLU activation)`
    - `Dropout (rate=0.5)`: 과적합 방지
    - `Dense (12 units, Softmax activation)`: 최종 12개 국가 분류
- **전체 파라미터 수**: 약 625만 개

---

## 5. 핵심 학습 전략

### 5.1. 입력 전처리 레이어
- `EfficientNetV2` 모델이 요구하는 특정 입력 범위(`-1` ~ `1`)에 맞추기 위해, 모델의 가장 첫 부분에 `Lambda` 레이어를 추가하여 `tf.keras.applications.efficientnet_v2.preprocess_input` 함수를 적용함. 이는 학습 성공의 가장 결정적인 요인이었음.

### 5.2. 데이터 증강 (Data Augmentation)
- 한정된 훈련 데이터를 최대한 활용하고 모델의 일반화 성능을 높이기 위해 다음 기법들을 적용함:
    - `RandomFlip("horizontal")`: 좌우 반전
    - `RandomRotation(0.1)`: ±10% 내외 회전
    - `RandomZoom(0.2)`: ±20% 내외 확대/축소
    - `RandomContrast(0.2)`: 대비(contrast) 무작위 변경
    - `RandomTranslation(height_factor=0.1, width_factor=0.1)`: 상하/좌우 10% 내외 이동

### 5.3. 2단계 전이학습 (2-Stage Transfer Learning)
- **1단계: 헤드 학습 (Feature Extraction)**
    - **목표**: 사전 학습된 `EfficientNetV2`의 몸통(base_model)은 완전히 동결(freeze)시키고, 새로 추가한 분류기 헤드만 훈련시켜 데이터의 전반적인 특징을 빠르게 학습.
    - **학습률**: `1e-3` (Adam Optimizer)
    - **Epochs**: 최대 30, `EarlyStopping`(patience=7)으로 조기 종료
- **2단계: 미세조정 (Fine-Tuning)**
    - **목표**: 1단계에서 똑똑해진 헤드는 유지한 채, 얼려두었던 `EfficientNetV2` 몸통의 상위 레이어들(약 70%)을 함께 훈련시켜 우리 데이터셋에 맞게 미세 조정.
    - **학습률**: `1e-4` (Adam Optimizer)
    - **Epochs**: 최대 100, 고급 콜백으로 자동 제어

### 5.4. 고급 훈련 콜백 (Advanced Callbacks)
- **`ModelCheckpoint`**: 훈련 과정 전체를 통틀어 `val_accuracy`(검증 정확도)가 가장 높았던 순간의 모델 가중치를 `best_model_ever.weights.h5` 파일에 자동으로 저장.
- **`ReduceLROnPlateau`**: `val_loss`(검증 손실)가 5번의 epoch 동안 개선되지 않으면, 학습률을 1/5로 자동으로 줄여 더 정교한 탐색을 유도.
- **`EarlyStopping`**: `val_loss`가 15번의 epoch 동안 개선되지 않으면, 불필요한 훈련을 중단하여 시간 낭비를 방지.

---

## 6. 웹 모델 추출 (Export)

- **추론 전용 모델 생성**: 최종 저장 전, `Random*`으로 시작하는 모든 데이터 증강 레이어를 제거하여 순수한 추론(Inference)용 모델을 새로 생성.
- **1차 저장 (TF SavedModel)**: Keras의 저장 방식과 변환 도구 간의 호환성 문제를 피하기 위해, 가장 안정적인 TensorFlow 네이티브 형식인 **`tf.saved_model.save()`**를 사용하여 모델을 임시 저장.
- **2차 변환 (TensorFlow.js)**:
    - **변환 도구**: `tensorflowjs_converter`
    - **입력 형식**: `tf_saved_model`
    - **출력 형식**: `tfjs_graph_model`
    - **결과물**: 웹 브라우저에서 직접 로드할 수 있는 `model.json`과 `shard` 파일들.

---

## 7. 최종 성능

- **테스트 정확도**: **49.50%**
- **평가**:
    - 무작위 추측(약 8.3%)보다는 훨씬 높으며, AI 모델이 데이터로부터 유의미한 패턴을 학습했음을 증명함.
    - `ethiopian`, `french`, `indian`, `japanese`, `saudi` 등의 클래스에서 50~70%대의 F1-score를 기록하며 유의미한 성능 향상을 보임.
    - 서비스의 재미 요소로는 활용 가능하나, 신뢰도 높은 과학적 근거로 사용하기에는 부족함.
- **향후 개선 방향**:
    - **데이터 확보**: 클래스당 최소 500~1000장 이상의 고품질 데이터 확보가 가장 시급하고 중요한 과제.
    - **클래스 재정의**: `british`, `french`처럼 구분이 어려운 클래스들을 '유럽계'와 같이 더 큰 범주로 통합하는 기획적 변경 고려.
    - **추가 하이퍼파라미터 튜닝**: 더 긴 학습 시간, 다른 옵티마이저, 더 정교한 학습률 스케줄링 등 적용. 