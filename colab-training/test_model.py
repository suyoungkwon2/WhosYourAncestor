"""
학습된 모델로 사진 테스트
Colab에서 사진을 업로드하여 예측 결과 확인
"""

import os
import json
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from google.colab import files
import gc

def setup_tensorflow():
    """TensorFlow 환경 설정"""
    print("🧪 모델 테스트 시작")
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

def load_trained_model():
    """학습된 모델 로드"""
    print("🤖 학습된 모델 로드 중...")
    
    # 모델 정보 로드
    try:
        with open('model_info_8countries.json', 'r') as f:
            model_info = json.load(f)
        print("✅ 모델 정보 로드 완료")
        print(f"📊 라벨: {model_info['labels']}")
        print(f"📊 입력 형태: {model_info['input_shape']}")
        print(f"📊 클래스 수: {model_info['num_classes']}")
    except FileNotFoundError:
        print("❌ model_info_8countries.json 파일을 찾을 수 없습니다.")
        print("📁 현재 디렉토리 파일들:")
        print(os.listdir('.'))
        return None, None
    
    # 모델 로드
    try:
        model = tf.keras.models.load_model('best_8countries_model.h5')
        print("✅ 모델 로드 완료")
        return model, model_info
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return None, None

def preprocess_image(image_path, target_size=(128, 128)):
    """이미지 전처리"""
    try:
        # 이미지 로드
        img = Image.open(image_path).convert('RGB')
        
        # 크기 조정
        img = img.resize(target_size)
        
        # 배열로 변환 및 정규화
        img_array = np.array(img) / 255.0
        
        # 배치 차원 추가
        img_array = np.expand_dims(img_array, axis=0)
        
        print(f"✅ 이미지 전처리 완료: {img_array.shape}")
        return img_array
        
    except Exception as e:
        print(f"❌ 이미지 전처리 실패: {e}")
        return None

def predict_image(model, image_array, model_info):
    """이미지 예측"""
    print("🔍 이미지 분석 중...")
    
    try:
        # 예측
        predictions = model.predict(image_array)
        
        # 결과 처리
        predicted_class = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class]
        
        # 모든 클래스의 확률
        class_probabilities = {}
        labels = model_info['labels']
        
        for i, (label, prob) in enumerate(zip(labels, predictions[0])):
            class_probabilities[label] = float(prob)
        
        # 결과 정렬 (확률 높은 순)
        sorted_results = sorted(class_probabilities.items(), key=lambda x: x[1], reverse=True)
        
        print(f"🎯 예측 결과:")
        print(f"  최고 확률: {labels[predicted_class]} ({confidence*100:.2f}%)")
        print(f"\n📊 모든 클래스 확률:")
        
        for label, prob in sorted_results:
            print(f"  {label}: {prob*100:.2f}%")
        
        return predicted_class, confidence, sorted_results
        
    except Exception as e:
        print(f"❌ 예측 실패: {e}")
        return None, None, None

def display_image_with_prediction(image_path, predicted_class, confidence, model_info):
    """이미지와 예측 결과 시각화"""
    try:
        # 이미지 로드
        img = Image.open(image_path)
        
        # 그래프 생성
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 이미지 표시
        ax1.imshow(img)
        ax1.set_title(f'업로드된 이미지')
        ax1.axis('off')
        
        # 예측 결과 표시
        labels = model_info['labels']
        predicted_label = labels[predicted_class]
        
        ax1.text(0.5, -0.1, f'예측: {predicted_label}\n확률: {confidence*100:.2f}%', 
                ha='center', transform=ax1.transAxes, fontsize=12, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        # 확률 분포 시각화
        labels_short = [label.replace('_female', '') for label in labels]
        probabilities = [class_probabilities[label] for label in labels]
        
        bars = ax2.bar(labels_short, probabilities)
        ax2.set_title('국가별 확률 분포')
        ax2.set_xlabel('국가')
        ax2.set_ylabel('확률')
        ax2.tick_params(axis='x', rotation=45)
        
        # 최고 확률 바 강조
        bars[predicted_class].set_color('red')
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"❌ 시각화 실패: {e}")

def test_with_uploaded_image():
    """업로드된 이미지로 테스트"""
    print("📤 이미지 업로드 중...")
    
    # 파일 업로드
    uploaded = files.upload()
    
    if not uploaded:
        print("❌ 파일이 업로드되지 않았습니다.")
        return
    
    # 업로드된 파일 경로
    image_path = list(uploaded.keys())[0]
    print(f"✅ 업로드된 파일: {image_path}")
    
    # 모델 로드
    model, model_info = load_trained_model()
    if model is None:
        print("❌ 모델을 로드할 수 없습니다.")
        return
    
    # 이미지 전처리
    image_array = preprocess_image(image_path)
    if image_array is None:
        print("❌ 이미지 전처리에 실패했습니다.")
        return
    
    # 예측
    predicted_class, confidence, sorted_results = predict_image(model, image_array, model_info)
    if predicted_class is None:
        print("❌ 예측에 실패했습니다.")
        return
    
    # 결과 시각화
    display_image_with_prediction(image_path, predicted_class, confidence, model_info)
    
    # 상세 결과 출력
    print(f"\n🎉 테스트 완료!")
    print(f"📊 예측된 국가: {model_info['labels'][predicted_class]}")
    print(f"📊 확률: {confidence*100:.2f}%")
    
    # 상위 3개 결과
    print(f"\n🏆 상위 3개 결과:")
    for i, (label, prob) in enumerate(sorted_results[:3]):
        print(f"  {i+1}. {label}: {prob*100:.2f}%")

def test_multiple_images():
    """여러 이미지로 테스트"""
    print("📤 여러 이미지 업로드 중...")
    
    # 파일 업로드
    uploaded = files.upload()
    
    if not uploaded:
        print("❌ 파일이 업로드되지 않았습니다.")
        return
    
    # 모델 로드
    model, model_info = load_trained_model()
    if model is None:
        print("❌ 모델을 로드할 수 없습니다.")
        return
    
    # 각 이미지 테스트
    for filename in uploaded.keys():
        print(f"\n{'='*50}")
        print(f"📸 테스트 중: {filename}")
        
        # 이미지 전처리
        image_array = preprocess_image(filename)
        if image_array is None:
            continue
        
        # 예측
        predicted_class, confidence, sorted_results = predict_image(model, image_array, model_info)
        if predicted_class is None:
            continue
        
        # 결과 출력
        predicted_label = model_info['labels'][predicted_class]
        print(f"🎯 결과: {predicted_label} ({confidence*100:.2f}%)")
        
        # 상위 3개 결과
        print(f"🏆 상위 3개:")
        for i, (label, prob) in enumerate(sorted_results[:3]):
            print(f"  {i+1}. {label}: {prob*100:.2f}%")

def main():
    """메인 실행 함수"""
    # TensorFlow 설정
    setup_tensorflow()
    
    print("\n🧪 테스트 옵션:")
    print("1. 단일 이미지 테스트")
    print("2. 여러 이미지 테스트")
    
    choice = input("선택하세요 (1 또는 2): ").strip()
    
    if choice == "1":
        test_with_uploaded_image()
    elif choice == "2":
        test_multiple_images()
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main() 