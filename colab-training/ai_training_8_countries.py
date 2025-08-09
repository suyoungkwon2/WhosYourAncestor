"""
8개 주요 국가만 사용한 AI 모델 학습
높은 정확도를 목표로 하는 집중 학습
"""

import os
import json
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import gc

def setup_tensorflow():
    """TensorFlow 환경 설정"""
    print("🚀 8개 국가 전용 AI 학습 시작")
    print("=" * 50)
    print("🔧 TensorFlow 환경 설정 중...")
    
    # 메모리 정리
    gc.collect()
    
    # GPU 메모리 설정
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print("✅ GPU 메모리 증가 설정 완료")
        except RuntimeError as e:
            print(f"⚠️ GPU 설정 오류: {e}")
    
    print(f"TensorFlow 버전: {tf.__version__}")
    print(f"GPU 사용 가능: {len(tf.config.list_physical_devices('GPU'))}")

def load_selected_countries_data():
    """선택된 8개 국가 데이터만 로드"""
    print("📂 8개 국가 데이터 로드 중...")
    
    # 선택된 8개 국가 (데이터가 많은 국가들)
    selected_countries = [
        'british', 'chinese', 'french', 'german', 
        'italian', 'japanese', 'korean', 'spanish'
    ]
    
    # 가능한 데이터 경로들
    possible_paths = [
        "/content/dataset",
        "/content/drive/MyDrive/WhosYourAncestor/data",
        "/content/drive/MyDrive/WhosYourAncestor",
        "/content/WhosYourAncestor/data",
        "/content/data",
        "/content"
    ]
    
    data_dir = None
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ 데이터 경로 발견: {path}")
            data_dir = path
            break
    
    if data_dir is None:
        print("❌ 데이터 경로를 찾을 수 없습니다.")
        raise FileNotFoundError("데이터 경로를 찾을 수 없습니다.")
    
    female_dir = os.path.join(data_dir, "female")
    
    if not os.path.exists(female_dir):
        print(f"❌ Female 폴더를 찾을 수 없습니다: {female_dir}")
        raise FileNotFoundError(f"Female 폴더를 찾을 수 없습니다: {female_dir}")
    
    images = []
    labels = []
    label_names = []
    
    print(f"📊 선택된 국가: {selected_countries}")
    
    for country in selected_countries:
        country_path = os.path.join(female_dir, country)
        if not os.path.exists(country_path):
            print(f"⚠️ {country} 폴더가 없습니다. 건너뜁니다.")
            continue
            
        files = [f for f in os.listdir(country_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"👩 {country} 처리 중... ({len(files)}개)")
        
        for file in files:
            try:
                image_path = os.path.join(country_path, file)
                img = Image.open(image_path).convert('RGB')
                img = img.resize((128, 128))  # 더 작은 이미지 사용
                img_array = np.array(img) / 255.0
                
                images.append(img_array)
                labels.append(country)
                label_names.append(f"{country}_female")
                
            except Exception as e:
                print(f"⚠️ 파일 로드 실패: {file} - {e}")
    
    return np.array(images), np.array(labels), label_names

def create_lightweight_model(num_classes):
    """가벼운 모델 생성"""
    print("🏗️ 가벼운 모델 생성 중...")
    
    model = tf.keras.Sequential([
        # 입력 레이어
        layers.Input(shape=(128, 128, 3)),
        
        # 첫 번째 컨볼루션 블록
        layers.Conv2D(32, 3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.2),
        
        # 두 번째 컨볼루션 블록
        layers.Conv2D(64, 3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.2),
        
        # 세 번째 컨볼루션 블록
        layers.Conv2D(128, 3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D(2),
        layers.Dropout(0.2),
        
        # 글로벌 풀링
        layers.GlobalAveragePooling2D(),
        
        # 완전 연결 레이어
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # 컴파일
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ 가벼운 모델 생성 완료")
    return model

def train_model_with_balanced_data(model, X_train, y_train, X_val, y_val, num_classes):
    """균형잡힌 데이터로 모델 학습"""
    print("🎯 균형잡힌 데이터로 모델 학습 시작...")
    
    # 적당한 데이터 증강
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        layers.RandomBrightness(0.2),
        layers.RandomContrast(0.2),
    ])
    
    # 콜백 설정
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=20,
            restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.7,
            patience=10,
            min_lr=1e-7
        ),
        tf.keras.callbacks.ModelCheckpoint(
            'best_8countries_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # 학습
    history = model.fit(
        data_augmentation(X_train),
        y_train,
        validation_data=(X_val, y_val),
        epochs=200,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

def evaluate_model(model, X_test, y_test, label_encoder):
    """모델 평가"""
    print("📊 모델 평가 중...")
    
    # 예측
    predictions = model.predict(X_test)
    y_pred = np.argmax(predictions, axis=1)
    
    # 정확도 계산
    accuracy = np.mean(y_pred == y_test)
    print(f"🎯 테스트 정확도: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # 클래스별 정확도
    from sklearn.metrics import classification_report
    class_names = label_encoder.classes_
    print("\n📈 클래스별 정확도:")
    print(classification_report(y_test, y_pred, target_names=class_names))
    
    return accuracy

def save_model_for_web(model, label_encoder, num_classes):
    """웹 배포용 모델 저장"""
    print("🌐 웹 배포용 모델 저장 중...")
    
    # 모델 정보 저장
    model_info = {
        "labels": [f"{label}_female" for label in label_encoder.classes_],
        "input_shape": [128, 128, 3],
        "num_classes": num_classes
    }
    
    with open('model_info_8countries.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    # TensorFlow.js 모델 변환
    import tensorflowjs as tfjs
    tfjs.converters.save_keras_model(model, 'web_model_8countries')
    
    print("✅ 웹 배포용 모델 저장 완료")

def plot_training_history(history):
    """학습 히스토리 시각화"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # 정확도
    ax1.plot(history.history['accuracy'], label='Training Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # 손실
    ax2.plot(history.history['loss'], label='Training Loss')
    ax2.plot(history.history['val_loss'], label='Validation Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('8countries_training_history.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """메인 실행 함수"""
    # TensorFlow 설정
    setup_tensorflow()
    
    # 데이터 로드
    images, labels, label_names = load_selected_countries_data()
    
    print(f"✅ 데이터 로드 완료: {len(images)}개")
    print(f"📊 데이터 형태: {images.shape}")
    print(f"🏷️ 라벨 개수: {len(set(labels))}")
    
    # 라벨 인코딩
    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(labels)
    num_classes = len(label_encoder.classes_)
    
    print(f"📈 국가별 데이터 분포:")
    for i, country in enumerate(label_encoder.classes_):
        count = np.sum(labels_encoded == i)
        print(f"  {country}: {count}개")
    
    # 데이터 분할
    X_train, X_temp, y_train, y_temp = train_test_split(
        images, labels_encoded, test_size=0.3, random_state=42, stratify=labels_encoded
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    
    print(f"📊 학습 데이터: {len(X_train)}개")
    print(f"📊 검증 데이터: {len(X_val)}개")
    print(f"📊 테스트 데이터: {len(X_test)}개")
    
    # 모델 생성
    model = create_lightweight_model(num_classes)
    
    # 모델 학습
    history = train_model_with_balanced_data(model, X_train, y_train, X_val, y_val, num_classes)
    
    # 모델 평가
    accuracy = evaluate_model(model, X_test, y_test, label_encoder)
    
    # 웹 배포용 모델 저장
    save_model_for_web(model, label_encoder, num_classes)
    
    # 학습 히스토리 시각화
    plot_training_history(history)
    
    print("\n🎉 8개 국가 모델 학습 완료!")
    print(f"📊 최종 정확도: {accuracy*100:.2f}%")
    print("📁 생성된 파일:")
    print("  - best_8countries_model.h5 (최고 성능 모델)")
    print("  - web_model_8countries/ (TensorFlow.js 모델)")
    print("  - model_info_8countries.json (모델 정보)")
    print("  - 8countries_training_history.png (학습 그래프)")

if __name__ == "__main__":
    main() 