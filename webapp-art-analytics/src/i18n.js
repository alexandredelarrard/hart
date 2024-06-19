import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpApi from 'i18next-http-backend';

// Import your translation files
import translationEN from './locales/en/translation.json';
import translationFR from './locales/fr/translation.json';

const resources = {
  en: {
    translation: translationEN,
  },
  fr: {
    translation: translationFR,
  },
};

i18n
  .use(initReactI18next) // Passes i18n down to react-i18next
  .use(LanguageDetector) // Detects the user language
  .use(HttpApi) // Loads translations using http (default public/assets/locals/{{lng}}/{{ns}}.json)
  .init({
    resources,
    fallbackLng: 'fr', // Use 'en' if the language is not available
    debug: true,
    // keySeparator: false, // this was the line that I've had to remove to make it work
    // keySeparator: '.', // if you want to re-enable it (not "true", but actual separator value)
    interpolation: {
      escapeValue: false, // React already safes from xss
    },
  });

export default i18n;