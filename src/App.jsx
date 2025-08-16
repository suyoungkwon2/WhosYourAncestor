import { useEffect, useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import { useTranslation } from 'react-i18next';
import { initModel, predict } from './ai_model.js';
import AncestryCard from './components/AncestryCard';
import LanguageSelector from './components/LanguageSelector';

function App() {
  const { t } = useTranslation();
  const [isModelLoading, setIsModelLoading] = useState(true);
  const [predictions, setPredictions] = useState([]);
  const [uploadedImage, setUploadedImage] = useState(null);
  const imageRef = useRef(null);
  const cardRef = useRef(null);
  
  useEffect(() => {
    initModel().then(() => {
      setIsModelLoading(false);
    });
  }, []);

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setPredictions([]);
    setUploadedImage(URL.createObjectURL(file)); 
  };
  
  const handlePredict = async () => {
    if (!imageRef.current) return;
    const results = await predict(imageRef.current);
    if(results) {
      setPredictions(results);
    }
  }

  const handleShare = async () => {
    if (!cardRef.current) return;
  
    try {
      const canvas = await html2canvas(cardRef.current, {
        useCORS: true,
        allowTaint: true,
        scale: 2, 
      });
      
      canvas.toBlob(async (blob) => {
        if (!blob) {
          alert('이미지 변환에 실패했습니다.');
          return;
        }
  
        const file = new File([blob], 'my-ancestry-card.png', { type: 'image/png' });
        
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({
            files: [file],
            title: '나의 조상 카드',
            text: 'AI로 내 얼굴의 혈통을 분석해봤어요!',
          });
        } else {
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = 'my-ancestry-card.png';
          link.click();
          URL.revokeObjectURL(link.href);
        }
      });
    } catch (error) {
      console.error('공유하기 실패:', error);
      alert('공유하는 중 오류가 발생했습니다.');
    }
  };

  const handleReset = () => {
    setPredictions([]);
    setUploadedImage(null);
  };

  return (
    <div className="min-h-screen bg-ivory py-8 px-4 font-sans">
      <div className="container max-w-md mx-auto">
        {!predictions.length ? (
          // 홈 화면 - 분석 전
          <>
            <div className="text-center mb-12">
              <p className="text-gray-600 mb-2">Select your language</p>
              <LanguageSelector />
            </div>

            <div className="text-center mb-8">
              <h1 className="text-5xl font-bold text-gray-800 mb-2">{t('home_title')}</h1>
              <p className="text-lg text-gray-600">{t('home_subtitle')}</p>
            </div>

            <div className="flex justify-center my-8">
              <img src="/img_passport.png" alt="Passport illustration" className="w-48 h-auto drop-shadow-lg" />
            </div>
            
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
              <div className="upload-box">
                <input 
                  type="file" 
                  id="imageUpload" 
                  accept="image/*" 
                  onChange={handleImageChange}
                  className="hidden" 
                />
                <label 
                  htmlFor="imageUpload" 
                  className="block w-full py-4 px-4 text-center bg-yellow-400 text-gray-800 rounded-xl cursor-pointer hover:bg-yellow-500 transition-colors text-xl font-bold"
                >
                  {t('button_select_photo')}
                </label>
                <p className="text-xs text-gray-500 mt-2 text-center">{t('privacy_notice')}</p>
              </div>
            </div>

            {isModelLoading && (
              <p className="text-center text-gray-600">
                {t('text_loading_model')}
              </p>
            )}

            {uploadedImage && !predictions.length && (
              <>
                <p className="text-center text-gray-600">{t('text_analyzing')}</p>
                {/* 분석을 위해 화면에는 보이지 않지만 로드되어야 하는 이미지 */}
                <img 
                  ref={imageRef} 
                  src={uploadedImage} 
                  alt="For analysis" 
                  className="hidden"
                  onLoad={handlePredict}
                />
              </>
            )}
          </>
        ) : (
          // 결과 화면 - 분석 후
          <>
            <AncestryCard
              ref={cardRef}
              image={uploadedImage}
              predictions={predictions}
              onShare={handleShare}
            />
            <button
              onClick={handleReset}
              className="mt-4 w-full py-3 px-4 bg-gray-400 text-white rounded-xl hover:bg-gray-500 transition-colors font-bold"
            >
              {t('button_try_again')}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
