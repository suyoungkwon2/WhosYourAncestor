import { useEffect, useState, useRef } from 'react';
import { initModel, predict } from './ai_model.js';

function App() {
  const [isModelLoading, setIsModelLoading] = useState(true);
  const [predictions, setPredictions] = useState([]);
  const [uploadedImage, setUploadedImage] = useState(null);
  const imageRef = useRef(null);
  
  // 웹사이트가 처음 실행될 때 딱 한 번 AI 모델을 로딩합니다.
  useEffect(() => {
    initModel().then(() => {
      setIsModelLoading(false);
    });
  }, []);

  // 파일 업로드 input의 내용이 바뀔 때 실행되는 함수
  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 예측 결과를 초기화하고, 업로드된 이미지 URL을 화면에 보여주기 위해 저장합니다.
    setPredictions([]);
    setUploadedImage(URL.createObjectURL(file)); 
  };
  
  // '분석하기' 버튼을 눌렀을 때 실행되는 함수
  const handlePredict = async () => {
    if (!imageRef.current) return;
    const results = await predict(imageRef.current);
    if(results) {
      setPredictions(results);
    }
  }

  return (
    <div className="container">
      <h1>당신의 조상은 어느 나라 사람일까요?</h1>
      <p className="subtitle">AI로 얼굴 사진을 분석하여 혈통을 예측해 보세요!</p>
      
      <div className="upload-box">
        <input type="file" id="imageUpload" accept="image/*" onChange={handleImageChange} />
        <label htmlFor="imageUpload" className="upload-label">
          사진 선택하기
        </label>
      </div>

      {isModelLoading && <p className="loading-text">AI 모델을 준비하는 중입니다... (약 10초 소요)</p>}
      
      {uploadedImage && (
        <div className="result-area">
          <img 
            ref={imageRef} 
            src={uploadedImage} 
            alt="Uploaded" 
            className="uploaded-image"
            onLoad={handlePredict} // 이미지가 화면에 완전히 로드되면 자동으로 분석 실행
          />
          
          {predictions.length > 0 ? (
            <div className="prediction-list">
              <h2>분석 결과</h2>
              <ul>
                {predictions.map((p, index) => (
                  <li key={index}>
                    <span className="country-name">{p.country.charAt(0).toUpperCase() + p.country.slice(1)}</span>
                    <div className="progress-bar-container">
                      <div 
                        className="progress-bar" 
                        style={{ width: `${p.probability * 100}%` }}
                      ></div>
                    </div>
                    <span className="percentage">{(p.probability * 100).toFixed(1)}%</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
             <p className="loading-text">이미지를 분석하는 중입니다...</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
