import axios from 'axios';

export const botController = async (req, res) => {
    try {
        const data = await axios.post('http://localhost:5001/chatbot', req.body);
        res.json(data.data); 
    } catch (error) {
        console.error('Error with Python server:', error);
        res.status(500).json({ error: 'Error with Python server' });
    }
}

