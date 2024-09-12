import axios from 'axios';
import Chat from '../Models/chatModel.js';


export const botController = async (req, res) => {
    try {
        const data = await axios.post('http://localhost:5001/chatbot', req.body);
        res.json(data.data); 

        // Save the chat to the database
        const chat = new Chat({
            message: req.body.message,
            user: req.user._id,
            botReply: data.data.response,
        });
        await chat.save();
        console.log('Chat saved to database');

    } catch (error) {
        console.error('Error with Python server:', error);
        res.status(500).json({ error: 'Error with Python server' });
    }
}

export const getChats = async (req, res) => {
    try {
        const chats = await Chat.find({ user: req.user._id });
        res.json(chats);
    } catch (error) {
        console.error('Error getting chats:', error);
        res.status(500).json({ error: 'Error getting chats' });
    }
}
