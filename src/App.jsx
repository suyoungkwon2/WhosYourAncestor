import { useEffect, useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import { useTranslation } from 'react-i18next';
import { initModel, predict } from './ai_model.js';
import AncestryCard from './components/AncestryCard';
import LanguageSelector from './components/LanguageSelector';
import InfoModal from './components/InfoModal';
import passportImage from '/img_passport.png'; // 경로 수정

function App() {
  const { t } = useTranslation();
  const [isModelLoading, setIsModelLoading] = useState(true);
  const [predictions, setPredictions] = useState([]);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [selectedGender, setSelectedGender] = useState('female');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const imageRef = useRef(null);
  const cardRef = useRef(null);
  const fileInputRef = useRef(null);
  
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

  const handleGenderSelect = (gender) => {
    if (gender === 'male') {
      setIsModalOpen(true);
    } else {
      setSelectedGender('female');
    }
  };

  const handleTryAgain = () => {
    fileInputRef.current?.click();
  };

  const handleGoHome = () => {
    setPredictions([]);
    setUploadedImage(null);
  };

  return (
    <div className="min-h-screen bg-ivory py-8 px-4 font-sans">
      <InfoModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={t('modal_title_notice')}
        content={t('modal_content_male_soon')}
      />
      {/* 파일 입력 요소를 항상 렌더링되도록 밖으로 이동 */}
      <input 
        ref={fileInputRef}
        type="file" 
        id="imageUpload" 
        accept="image/*" 
        onChange={handleImageChange}
        className="hidden" 
      />
      <div className="container max-w-md mx-auto">
        {!predictions.length ? (
          // 홈 화면 - 분석 전
          <>
            <div className="text-center mb-8">
              <p className="text-gray-600 mb-2">Select your language</p>
              <LanguageSelector />
            </div>

            <div className="text-center mb-8">
              <h1 className="text-5xl font-bold text-gray-800 mb-2">{t('home_title')}</h1>
              <p className="text-lg text-gray-600">{t('home_subtitle')}</p>
            </div>

            <div className="flex justify-center my-8">
              <img src={passportImage} alt="Passport illustration" className="w-48 h-auto drop-shadow-lg" />
            </div>
            
            <div className="flex justify-center space-x-4 mb-6">
              <button
                onClick={() => handleGenderSelect('female')}
                className={`py-2 px-6 rounded-full text-lg transition-colors ${selectedGender === 'female' ? 'bg-purple-500 text-white font-bold' : 'bg-gray-200'}`}
              >
                <span className="mr-2">♀</span>{t('gender_female')}
              </button>
              <button
                onClick={() => handleGenderSelect('male')}
                className="py-2 px-6 rounded-full text-lg bg-gray-200 transition-colors"
              >
                <span className="mr-2">♂</span>{t('gender_male')}
              </button>
            </div>

            <div className="upload-box px-4">
              <label 
                htmlFor="imageUpload" 
                className="block w-full py-4 px-4 text-center bg-purple-500 text-white rounded-xl cursor-pointer hover:bg-purple-600 transition-colors text-xl font-bold"
              >
                {t('button_select_photo')}
              </label>
              <p className="text-xs text-gray-500 mt-2 text-center">{t('privacy_notice')}</p>
            </div>

            {isModelLoading && (
              <p className="text-center text-gray-600 mt-8">
                {t('text_loading_model')}
              </p>
            )}

            {uploadedImage && !predictions.length && (
              <>
                <p className="text-center text-gray-600 mt-8">{t('text_analyzing')}</p>
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
              onClick={handleTryAgain}
              className="mt-4 w-full py-2 px-4 bg-gray-500 text-white rounded-xl hover:bg-gray-600 transition-colors font-bold text-lg"
            >
              {t('button_try_again')}
            </button>
            <button
              onClick={handleGoHome}
              className="mt-2 w-full text-center text-sm text-gray-500 hover:text-gray-700 underline"
            >
              {t('button_go_home')}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
