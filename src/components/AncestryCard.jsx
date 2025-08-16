import React, { forwardRef } from 'react';
import { countryData } from '../countryData';

const AncestryCard = forwardRef(({ image, predictions, onShare }, ref) => {
  // 상위 5개 국가만 표시
  const topPredictions = predictions.slice(0, 5);
  
  // 임시 해석 텍스트 생성
  const getInterpretation = () => {
    const topCountry = predictions[0];
    const topCountryInfo = countryData[topCountry.country.replace('_female', '')];
    return `당신의 얼굴은 ${topCountryInfo.name} 사람과 가장 닮았네요! ${(topCountry.probability * 100).toFixed(1)}%의 유사도를 보입니다. 특히 ${topCountryInfo.name} 사람들의 특징적인 이목구비가 잘 나타나고 있어요.`;
  };

  return (
    <div ref={ref} className="ancestry-card bg-white rounded-xl shadow-lg p-6 max-w-sm mx-auto">
      <h2 className="text-2xl font-bold text-center mb-4">나의 조상 카드</h2>
      
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
          const data = countryData[countryName] || { emoji: '🏳️', color: '#cccccc', name: countryName };
          
          return (
            <div key={index}>
              <div className="flex justify-between items-baseline mb-1">
                <span className="flex items-center text-base font-medium text-gray-700">
                  <span className="text-2xl mr-3">{data.emoji}</span>
                  {data.name}
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
          #조상찾기
        </span>
        <span className="bg-blue-100 text-blue-800 text-xs px-2.5 py-1 rounded-full">
          #AI얼굴분석
        </span>
        <span className="bg-blue-100 text-blue-800 text-xs px-2.5 py-1 rounded-full">
          #{countryData[predictions[0]?.country.replace('_female', '')]?.name}
        </span>
      </div>

      {/* 공유하기 버튼 */}
      <button
        onClick={onShare}
        className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors"
      >
        공유하기
      </button>
    </div>
  );
});

export default AncestryCard; 