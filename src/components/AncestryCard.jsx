import React, { forwardRef } from 'react';
import { useTranslation } from 'react-i18next';
import { countryData } from '../countryData';

const AncestryCard = forwardRef(({ image, predictions, onShare }, ref) => {
  const { t } = useTranslation();
  // 상위 5개 국가만 표시
  const topPredictions = predictions.slice(0, 5);
  
  // 임시 해석 텍스트 생성
  const getInterpretation = () => {
    const topCountry = predictions[0];
    const topCountryInfo = countryData[topCountry.country.replace('_female', '')];
    
    return t('card_interpretation', {
      country: t(topCountryInfo.nameKey),
      percent: (topCountry.probability * 100).toFixed(1)
    });
  };

  return (
    <div ref={ref} className="ancestry-card bg-white rounded-xl shadow-lg p-6 max-w-sm mx-auto">
      <h2 className="text-2xl font-bold text-center mb-4">{t('card_title')}</h2>
      
      {/* 업로드된 이미지 */}
      <div className="relative w-full aspect-square mb-4 rounded-lg overflow-hidden">
        <img 
          src={image} 
          alt="Uploaded face" 
          className="w-full h-full object-cover"
        />
      </div>

      {/* 분석 결과 */}
      <div className="space-y-4 mb-5">
        {topPredictions.map((p, index) => {
          const countryName = p.country.replace('_female', '');
          const data = countryData[countryName] || { emoji: '🏳️', color: '#cccccc', nameKey: 'country_unknown' };
          
          return (
            <div key={index}>
              <div className="flex justify-between items-baseline mb-1">
                <span className="flex items-center text-base font-medium text-gray-700">
                  <span className="text-2xl mr-3">{data.emoji}</span>
                  {t(data.nameKey)}
                </span>
                <span className="text-xl font-bold" style={{ color: data.color }}>
                  {(p.probability * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="h-3 rounded-full" 
                  style={{ 
                    width: `${p.probability * 100}%`,
                    backgroundColor: data.color
                  }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 해석 텍스트 */}
      <p className="text-gray-700 text-sm mb-4">
        {getInterpretation()}
      </p>

      {/* 해시태그 */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="bg-blue-100 text-blue-800 text-xs px-2.5 py-1 rounded-full">
          {t('hashtag_ancestry')}
        </span>
        <span className="bg-blue-100 text-blue-800 text-xs px-2.5 py-1 rounded-full">
          {t('hashtag_ai_face')}
        </span>
        <span className="bg-blue-100 text-blue-800 text-xs px-2.5 py-1 rounded-full">
          #{t(countryData[predictions[0]?.country.replace('_female', '')]?.nameKey)}
        </span>
      </div>

      {/* 공유하기 버튼 */}
      <button
        onClick={onShare}
        className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors"
      >
        {t('button_share')}
      </button>
    </div>
  );
});

export default AncestryCard; 