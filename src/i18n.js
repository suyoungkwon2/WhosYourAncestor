import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from './locales/en/translation.json';
import ko from './locales/ko/translation.json';
import zh from './locales/zh/translation.json';
import ja from './locales/ja/translation.json';
import hi from './locales/hi/translation.json';
import es from './locales/es/translation.json';


i18n
  .use(initReactI18next)
  .init({
    lng: 'en', // 기본 언어
    fallbackLng: 'en', // lng에서 찾을 수 없을 때 사용할 언어
    debug: true,
    interpolation: {
      escapeValue: false, // React는 이미 XSS 방지를 하므로 false로 설정
    },
    resources: {
      en: { translation: en },
      ko: { translation: ko },
      zh: { translation: zh },
      ja: { translation: ja },
      hi: { translation: hi },
      es: { translation: es },
    },
  });

export default i18n; 