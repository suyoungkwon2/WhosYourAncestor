import React from 'react';
import { useTranslation } from 'react-i18next';

const InfoModal = ({ isOpen, onClose, title, content }) => {
  const { t } = useTranslation();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-sm mx-4">
        <h3 className="text-xl font-bold mb-4">{title}</h3>
        <p className="text-gray-700 mb-6">{content}</p>
        <button
          onClick={onClose}
          className="w-full bg-gray-500 text-white py-2 rounded-lg hover:bg-gray-600 transition-colors"
        >
          {t('button_close')}
        </button>
      </div>
    </div>
  );
};

export default InfoModal; 