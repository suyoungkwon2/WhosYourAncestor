# 셀 1: 라이브러리 설치 (단순화)
!pip install -q tensorflowjs

# 셀 2: 기본 설정 및 임포트

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
    """TensorFlow 및 GPU 환경을 설정합니다."""
    print("🚀 고급 AI 학습 스크립트 시작 (12개국 버전)")
    print("=" * 60)
    print("🔧 TensorFlow 환경 설정 중...")
    
    gc.collect()
    tf.keras.backend.clear_session()

    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print("✅ GPU 메모리 증가 설정 완료")
        except RuntimeError as e:
            print(f"⚠️ GPU 설정 오류: {e}")
    
    print(f"TensorFlow 버전: {tf.__version__}")
    print(f"GPU 사용 가능: {len(tf.config.list_physical_devices('GPU')) > 0}")
    print("=" * 60)

    # 셀 3: 데이터 로드 함수 정의 (최종 수정 버전)

def load_selected_countries_data():
    """선택된 12개 국가 데이터만 로드합니다."""
    print("📂 12개 국가 데이터 로드 중...")
    
    selected_countries = [
        'british', 'chinese', 'ethiopian', 'french', 'indian', 
        'indigenous', 'japanese', 'korean', 'mexican', 
        'nigerian', 'russian', 'saudi'
    ]
    
    # !!! 중요 !!!
    # 캐글에 올린 데이터셋 이름으로 이 경로를 수정해주세요!
    data_dir = "/kaggle/input/8-countries-female-faces" # <--- 이 부분을 자신의 데이터셋 경로로 수정하세요!
    
    print(f"✅ 데이터 경로 설정: {data_dir}")
    female_dir = os.path.join(data_dir, "female")
    
    if not os.path.exists(female_dir):
        print(f"❌ '{female_dir}' 경로를 찾을 수 없습니다.")
        if os.path.exists(data_dir): print(f"📁 '{data_dir}' 폴더 내용: {os.listdir(data_dir)}")
        raise FileNotFoundError(f"Female 폴더를 찾을 수 없습니다: {female_dir}")
        
    images, labels = [], []
    print(f"📊 선택된 국가: {selected_countries}")

    for country in selected_countries:
        country_path = os.path.join(female_dir, country)
        if not os.path.exists(country_path):
            print(f"⚠️ {country} 폴더가 없어 건너뜁니다.")
            continue
            
        files = [f for f in os.listdir(country_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"👩 {country} 처리 중... ({len(files)}개)")
        
        for file in files:
            try:
                img = Image.open(os.path.join(country_path, file)).convert('RGB')
                img = img.resize((224, 224))
                images.append(np.array(img))
                labels.append(country)
            except Exception as e:
                print(f"⚠️ 파일 로드 실패: {file} - {e}")
    
    return np.array(images) / 255.0, np.array(labels)


# 셀 4: 모델 생성 함수 수정 (데이터 증강 강화)

def build_model(num_classes):
    """EfficientNetV2를 베이스로 하는 강력한 모델을 생성합니다."""
    print("🏗️ EfficientNetV2 전문가 모델 생성 중 (증강 강화 버전)...")
    
    base_model = tf.keras.applications.efficientnet_v2.EfficientNetV2B0(
        include_top=False,
        weights='imagenet',
        input_shape=(224, 224, 3),
        pooling='avg'
    )
    base_model.trainable = False
    base_model._name = "efficientnetv2-b0"

    model = tf.keras.Sequential([
        layers.Input(shape=(224, 224, 3)),
        layers.Lambda(lambda x: tf.keras.applications.efficientnet_v2.preprocess_input(x * 255.0), name="preprocess_input"),
        
        # --- 데이터 증강 강화 ---
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.2),      # Zoom 범위를 약간 늘림
        layers.RandomContrast(0.2),  # 대비(contrast) 증강 추가
        layers.RandomTranslation(height_factor=0.1, width_factor=0.1), # 상하/좌우 이동 증강 추가
        
        base_model,
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax")
    ], name="Ancestor_Identifier_V2")
    
    print("✅ 모델 생성 완료")
    return model

def evaluate_model(model, X_test, y_test_one_hot, label_encoder):
    """미세 조정된 모델을 평가합니다."""
    print("\n📊 모델 평가 중...")
    
    y_pred_probs = model.predict(X_test, verbose=1)
    y_pred = np.argmax(y_pred_probs, axis=1)
    y_true = np.argmax(y_test_one_hot, axis=1)

    accuracy = np.mean(y_pred == y_true)
    print(f"🎯 테스트 정확도: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    from sklearn.metrics import classification_report
    class_names = label_encoder.classes_
    print("\n📈 클래스별 정확도:")
    print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))
    return accuracy



# 셀 5: 결과 시각화 함수 정의

def plot_training_history(history, fine_tune_history, initial_epochs):
    """두 단계 학습 히스토리를 합쳐서 시각화합니다."""
    acc = history.history['accuracy'] + fine_tune_history.history['accuracy']
    val_acc = history.history['val_accuracy'] + fine_tune_history.history['val_accuracy']
    loss = history.history['loss'] + fine_tune_history.history['loss']
    val_loss = history.history['val_loss'] + fine_tune_history.history['val_loss']

    plt.figure(figsize=(15, 6))

    plt.subplot(1, 2, 1)
    plt.plot(acc, label='Training Accuracy')
    plt.plot(val_acc, label='Validation Accuracy')
    plt.ylim([min(plt.ylim()) * 0.9, 1.0])
    plt.axvline(initial_epochs - 1, color='gray', linestyle='--', label='Start Fine-Tuning')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(loss, label='Training Loss')
    plt.plot(val_loss, label='Validation Loss')
    plt.axvline(initial_epochs - 1, color='gray', linestyle='--', label='Start Fine-Tuning')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('advanced_training_history_12_countries.png', dpi=300)
    plt.show()



    # 셀 6: 메인 실행 로직 수정 (고급 훈련 적용)

def main_final_improved():
    setup_tensorflow()
    
    # --- 데이터 준비 (이전과 동일) ---
    images, labels_str = load_selected_countries_data()
    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(labels_str)
    num_classes = len(label_encoder.classes_)
    y_one_hot = tf.keras.utils.to_categorical(labels_encoded, num_classes)
    
    X_train, X_temp, y_train, y_temp = train_test_split(
        images, y_one_hot, test_size=0.2, random_state=42, stratify=y_one_hot)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
    print(f"📊 학습: {len(X_train)}, 검증: {len(X_val)}, 테스트: {len(X_test)}")
    
    # --- 모델 생성 ---
    global model 
    model = build_model(num_classes)
    
    # --- 1단계: 헤드 학습 ---
    print("\n--- 🚀 1단계: 분류기 헤드 학습 ---")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
        metrics=['accuracy']
    )
    early_stop_s1 = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=7, verbose=1, restore_best_weights=True)
    history_s1 = model.fit(X_train, y_train, epochs=30, validation_data=(X_val, y_val), batch_size=32, verbose=1, callbacks=[early_stop_s1])
    
    # --- 2단계: 미세조정 (고급 콜백 적용) ---
    print("\n--- 🚀 2단계: 전체 모델 미세조정 ---")
    base_model = model.get_layer("efficientnetv2-b0") 
    base_model.trainable = True
    
    # 더 많은 레이어를 fine-tuning (하위 30%만 동결)
    fine_tune_layers = int(len(base_model.layers) * 0.3)
    for layer in base_model.layers[:fine_tune_layers]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
        metrics=['accuracy']
    )
    model.summary()
    
    # --- "똑똑한 학습 조교" 콜백 설정 ---
    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        'best_model_ever.weights.h5', monitor='val_accuracy', save_best_only=True, 
        save_weights_only=True, mode='max', verbose=1)
    
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.2, patience=5, verbose=1, min_lr=1e-6)
        
    early_stop_s2 = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, verbose=1)

    history_s2 = model.fit(
        X_train, y_train, epochs=100, validation_data=(X_val, y_val), 
        batch_size=32, verbose=1, callbacks=[checkpoint, reduce_lr, early_stop_s2])
    
    # --- 최고 성능 모델 로드 및 평가 ---
    print("\n✨ 훈련 과정 중 가장 성능이 좋았던 모델의 가중치를 불러옵니다...")
    model.load_weights('best_model_ever.weights.h5')
    
    global final_accuracy, label_encoder_global, num_classes_global, X_test_global, y_test_global
    final_accuracy = evaluate_model(model, X_test, y_test, label_encoder)
    label_encoder_global = label_encoder
    num_classes_global = num_classes
    X_test_global = X_test
    y_test_global = y_test

# 메인 함수 호출
if __name__ == '__main__' and 'get_ipython' in locals():
    try:
        main_final_improved()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()



# 셀 7: 파일 업로드 전용

import ipywidgets as widgets
from IPython.display import display

# uploader 위젯을 다른 셀에서도 사용할 수 있도록 전역 변수로 선언합니다.
global uploader
uploader = widgets.FileUpload(
    accept='image/*',
    multiple=False,
    description='사진 업로드'
)

print("1. 아래 버튼을 눌러 테스트할 사진을 업로드하세요.")
print("2. 업로드가 완료되면, 다음 셀(8번 셀)을 실행하여 결과를 확인하세요.")
display(uploader)


# 셀 8: 예측 실행 및 결과 확인 (버그 수정 버전)

import io
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# 이전 셀(7번 셀)에서 파일이 업로드되었는지 확인합니다.
if not uploader.value:
    print("오류: 이전 셀에서 사진을 먼저 업로드해주세요.")
else:
    # --- 핵심 버그 수정 ---
    # uploader.value는 튜플이므로, 첫 번째 항목을 가져옵니다.
    uploaded_file_info = uploader.value[0] 
    
    # 이제 딕셔너리에서 파일 이름과 내용을 추출합니다.
    fn = uploaded_file_info['name']
    content = uploaded_file_info['content']
    
    print(f"'{fn}' 파일에 대한 예측을 시작합니다...")
    
    # 1. 이미지 불러오기 및 전처리
    img = Image.open(io.BytesIO(content)).convert('RGB')
    img_resized = img.resize((224, 224))
    img_array = np.array(img_resized) / 255.0
    img_batch = np.expand_dims(img_array, axis=0)

    # 2. 예측 실행
    predictions = model.predict(img_batch)
    
    # 3. 결과 해석 및 출력
    top_k = 5
    top_indices = np.argsort(predictions[0])[::-1][:top_k]
    class_names = label_encoder_global.classes_
    
    print("\n--- 예측 결과 (Top 5) ---")
    for i, idx in enumerate(top_indices):
        class_name = class_names[idx]
        probability = predictions[0][idx] * 100
        print(f"{i+1}. {class_name.capitalize()}: {probability:.2f}%")
        
    # 4. 업로드된 이미지와 결과 함께 표시
    plt.figure(figsize=(6, 6))
    plt.imshow(img)
    plt.title(f"Uploaded: {fn}\nTop Prediction: {class_names[top_indices[0]].capitalize()} ({predictions[0][top_indices[0]]*100:.2f}%)")
    plt.axis('off')
    plt.show()

    # 다음 테스트를 위해 업로드 위젯의 값을 초기화합니다.
    uploader.value.clear()
    uploader._counter = 0


    # 셀 9: 웹 배포용 모델 저장 (TF 직접 저장)

import json
import tensorflow as tf
import os
import shutil

print("\n🌐 웹 배포용 모델 저장 준비 중 (TF 직접 저장 방식)...")

# --- 1. 이전 결과물 청소 ---
if os.path.exists('tf_saved_model'):
    shutil.rmtree('tf_saved_model')
    print("🧹 이전 임시 SavedModel 폴더 삭제 완료.")
if os.path.exists('web_model_12_countries'):
    shutil.rmtree('web_model_12_countries')
    print("🧹 이전 TF.js 모델 폴더 삭제 완료.")

# --- 2. 추론 전용 모델 생성 (이전과 동일) ---
input_tensor = tf.keras.Input(shape=(224, 224, 3), name="input_tensor")
x = input_tensor
for layer in model.layers:
    if not layer.name.startswith('random'):
        x = layer(x)
inference_model = tf.keras.Model(inputs=input_tensor, outputs=x, name="Ancestor_Inference_Model")
print("\n--- 추론 전용 모델 구조 ---")
inference_model.summary(line_length=100)

# --- 3. 모델을 TensorFlow의 기본 SavedModel 형식으로 직접 저장 ---
saved_model_path = 'tf_saved_model'
print(f"\n1. 모델을 TensorFlow SavedModel 형식인 '{saved_model_path}'(으)로 저장합니다...")
try:
    # --- 핵심 수정: model.save() -> tf.saved_model.save() ---
    tf.saved_model.save(inference_model, saved_model_path)
    print(f"✅ '{saved_model_path}' 폴더 저장 완료!")

    # --- 4. 저장된 SavedModel을 TensorFlow.js Graph Model 형식으로 변환 ---
    output_dir = 'web_model_12_countries'
    print(f"\n2. '{saved_model_path}' 폴더를 TF.js Graph Model 형식인 '{output_dir}'(으)로 변환합니다...")
    
    import subprocess
    result = subprocess.run(
        [
            'tensorflowjs_converter', 
            '--input_format=tf_saved_model', 
            saved_model_path, 
            output_dir
        ],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ TensorFlow.js 모델 변환 성공!")
    else:
        print("❌ TensorFlow.js 모델 변환 실패!")
        print("\n--- 오류 내용 ---")
        print(result.stderr)

except Exception as e:
    print(f"\n❌ 모델 저장 또는 변환 중 치명적인 오류 발생: {e}")
    import traceback
    traceback.print_exc()

# --- 5. 최종 생성된 파일 목록과 모델 정보 JSON 파일을 저장합니다. ---
model_info = {
    "labels": [f"{label}_female" for label in label_encoder_global.classes_],
    "input_shape": [224, 224, 3], 
    "num_classes": num_classes_global
}
with open('model_info_12_countries.json', 'w') as f:
    json.dump(model_info, f, indent=2)

print("\n--- 최종 생성된 파일 목록 (/kaggle/working/) ---")
for item in sorted(os.listdir('/kaggle/working')):
    print(item)


    
# 셀 10: 웹 배포용 모델 폴더 압축

import shutil

# '/kaggle/working/web_model_12_countries' 폴더를
# '/kaggle/working/web_model_12_countries.zip' 파일로 압축합니다.
try:
    shutil.make_archive('web_model_12_countries', 'zip', '/kaggle/working/web_model_12_countries')
    print("✅ 'web_model_12_countries.zip' 파일 생성 완료!")
    print("이제 오른쪽 'Data' -> 'Output' 섹션에서 zip 파일을 다운로드하세요.")
except Exception as e:
    print(f"❌ 압축 중 오류 발생: {e}")
