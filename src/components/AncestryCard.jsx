import React, { forwardRef } from 'react';
import { useTranslation } from 'react-i18next';
import { countryData } from '../countryData';

const AncestryCard = forwardRef(({ image, predictions, onShare }, ref) => {
  const { t } = useTranslation();
  const topPredictions = predictions.slice(0, 5);

  const getInterpretation = () => {
    if (!predictions || predictions.length === 0) return "";
    const p1 = predictions[0];
    const p2 = predictions.length > 1 ? predictions[1] : null;
    const prob1 = p1.probability * 100;
    const prob2 = p2 ? p2.probability * 100 : 0;
    const country1Info = countryData[p1.country.replace('_female', '')];
    const country2Info = p2 ? countryData[p2.country.replace('_female', '')] : null;
    const country1Name = t(country1Info.nameKey);
    const country2Name = country2Info ? t(country2Info.nameKey) : '';
    if (prob1 > 90) return t('interpretation_pure', { country: country1Name, percent: prob1.toFixed(1) });
    if (prob1 > 70) return t('interpretation_dominant', { country: country1Name, percent: prob1.toFixed(1) });
    if (prob1 < 50 && p2 && (prob1 - prob2) < 10) return t('interpretation_balanced', { country1: country1Name, country2: country2Name });
    if (p2 && (prob1 + prob2) > 60 && (prob1 - prob2) > 10) return t('interpretation_clear_top_two', { country1: country1Name, country2: country2Name });
    if (prob1 < 30) return t('interpretation_global');
    return t('interpretation_default', { country: country1Name, percent: prob1.toFixed(1) });
  };

  return (
    <div ref={ref} className="ancestry-card bg-white rounded-xl shadow-lg p-6 max-w-sm mx-auto">
      <h2 className="text-2xl font-bold text-center mb-4">{t('card_title')}</h2>
      
      <div className="relative w-full aspect-square mb-4 rounded-lg overflow-hidden">
        <img 
          src={image} 
          alt="Uploaded face" 
          className="w-full h-full object-cover"
        />

        {/* 전체 오버레이 및 중앙 정렬 컨테이너 */}
        <div className="absolute inset-0 flex items-center justify-center bg-black/30 p-4">
          <div className="w-full space-y-3">
            {topPredictions.map((p, index) => {
              const countryName = p.country.replace('_female', '');
              const data = countryData[countryName] || { emoji: '🏳️', color: '#cccccc', nameKey: 'country_unknown' };
              
              return (
                <div key={index}>
                  <div className="flex justify-between items-baseline mb-1 text-white">
                    <span className="flex items-center text-base font-bold text-shadow">
                      <span className="text-2xl mr-2">{data.emoji}</span>
                      {t(data.nameKey)}
                    </span>
                    <span className="text-lg font-bold text-shadow">
                      {(p.probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200/30 rounded-full h-2.5">
                    <div 
                      className="h-2.5 rounded-full" 
                      style={{ 
                        width: `${p.probability * 100}%`,
                        backgroundColor: data.color,
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <p className="text-gray-700 text-sm mb-4 text-center">
        {getInterpretation()}
      </p>

      {/* 해시태그 */}
      <div className="flex flex-wrap gap-2 mb-4 justify-center">
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
        className="w-full bg-purple-500 text-white py-3 rounded-xl hover:bg-purple-600 transition-colors text-lg font-bold"
      >
        {t('button_share')}
      </button>
    </div>
  );
});

export default AncestryCard; 