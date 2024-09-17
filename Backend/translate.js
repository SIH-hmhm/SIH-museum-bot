import { v2 } from '@google-cloud/translate';
const { Translate } = v2;
import serviceKey from './serviceKey.json' assert { type: 'json' };

const translate = new Translate({
    credentials: serviceKey  // Using the imported JSON as credentials
});
  
const translateText = async (text, targetLanguage) => {
  try {
      console.log("Original Text :>", text);
      
      // Translate text with automatic source language detection
      const [translation, response] = await translate.translate(text, targetLanguage);

      // Log detected language
      console.log("Detected Language:>", response.data.translations[0].detectedSourceLanguage);
      const detectedLanguage = response.data.translations[0].detectedSourceLanguage;

      return {
          translation,
          detectedLanguage
      };
      
  } catch (err) {
      console.error('ERROR:', err);
  }
};

export default translateText;