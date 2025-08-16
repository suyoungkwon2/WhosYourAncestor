import React from 'react';
import { useTranslation } from 'react-i18next';

const languages = [
  { code: 'ko', name: '🇰🇷' },
  { code: 'en', name: '🇺🇸' },
  { code: 'zh', name: '🇨🇳' },
  { code: 'ja', name: '🇯🇵' },
  { code: 'hi', name: '🇮🇳' },
  { code: 'es', name: '🇪🇸' },
];

const LanguageSelector = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex justify-center space-x-4 my-4">
      {languages.map((lng) => (
        <button
          key={lng.code}
          onClick={() => changeLanguage(lng.code)}
          className={`text-3xl p-2 rounded-full transition-transform transform hover:scale-125 ${i18n.language === lng.code ? 'bg-white bg-opacity-50' : ''}`}
          title={lng.name}
        >
          {lng.name}
        </button>
      ))}
    </div>
  );
};

export default LanguageSelector; 