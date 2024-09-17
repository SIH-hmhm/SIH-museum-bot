import axios from 'axios';
import Chat from '../Models/chatModel.js';
import translateText from '../translate.js';

export const botController = async (req, res) => {
    try {
        // Translate the user's message to English
        const translatedMessage = await translateText(req.body.message, 'en');
        const detectedLanguage = translatedMessage.detectedLanguage;  // Extract detected language
        console.log('Detected Language:', detectedLanguage);
        console.log('Translated Message:', translatedMessage.translation);

        // Create payload with translated message
        const payload = {
            message: translatedMessage.translation,
        };
        console.log('Payload:', payload);

        // Send translated message to the chatbot (Python server)
        const { data } = await axios.post('http://localhost:5001/chatbot', payload);
        console.log('Chatbot Response:', data.response);

        // Translate the bot's response back to the detected language of the user
        const translatedResponse = await translateText(data.response, detectedLanguage);
        const finalResponse = translatedResponse.translation;  // Translated bot's response
        console.log('Translated Bot Response:', finalResponse);

        // Send the translated bot response back to the user
        res.json({ response: finalResponse });

        // Save the chat to the database (uncommented the chat saving logic)
        const chat = new Chat({
            message: req.body.message,  // Original message from the user
            user: req.user._id,         // Assuming req.user contains the user's ID
            botReply: finalResponse,    // Translated bot's reply
        });
        await chat.save();
        console.log('Chat saved to database');

    } catch (error) {
        console.error('Error with Python server:', error);
        res.status(500).json({ error: 'Error with Python server' });
    }
};

export const getChats = async (req, res) => {
    try {
        // Fetch chats specific to the user
        const chats = await Chat.find({ user: req.user._id });
        res.json(chats);
    } catch (error) {
        console.error('Error getting chats:', error);
        res.status(500).json({ error: 'Error getting chats' });
    }
};
