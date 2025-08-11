import * as tf from '@tensorflow/tfjs';

let model;
let labels;

/**
 * 웹사이트가 시작될 때 AI 모델과 라벨 정보를 미리 불러옵니다.
 */
export async function initModel() {
  if (model) return;

  try {
    console.log("AI Graph 모델 로딩을 시작합니다...");
    
    // --- 핵심 수정: tf.loadLayersModel -> tf.loadGraphModel ---
    const modelURL = '/web_model_12_countries/model.json';
    model = await tf.loadGraphModel(modelURL);

    const labelsURL = '/model_info_12_countries.json';
    const response = await fetch(labelsURL);
    const modelInfo = await response.json();
    labels = modelInfo.labels;

    console.log("AI Graph 모델 로딩이 완료되었습니다.");
    
    // 웜업: 첫 예측 속도를 높이기 위해 미리 한 번 실행합니다.
    tf.tidy(() => {
      model.predict(tf.zeros([1, 224, 224, 3]));
    });

  } catch (error) {
    console.error("AI 모델 로딩에 실패했습니다:", error);
  }
}

/**
 * 사용자가 업로드한 이미지를 받아 국적 예측을 수행합니다.
 */
export async function predict(imageElement) {
  if (!model) {
    console.error("모델이 아직 로드되지 않았습니다.");
    return null;
  }

  console.log("이미지 예측을 시작합니다...");

  const tensor = tf.tidy(() => {
    const img = tf.browser.fromPixels(imageElement).resizeNearestNeighbor([224, 224]).toFloat().div(tf.scalar(255.0));
    return img.expandDims(0);
  });

  // GraphModel은 predict 또는 execute를 사용합니다. predict가 동일하게 동작합니다.
  const predictions = await model.predict(tensor).data();
  tensor.dispose();

  const results = Array.from(predictions)
    .map((probability, index) => ({
      country: labels[index].replace('_female', ''),
      probability,
    }))
    .sort((a, b) => b.probability - a.probability)
    .slice(0, 5);

  console.log("예측 완료:", results);
  return results;
}