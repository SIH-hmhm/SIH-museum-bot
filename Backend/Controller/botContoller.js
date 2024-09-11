const axios = require('axios');

const botController = async (req, res) => {
    try {
        const axiosResponse = await axios.post('http://localhost:5001/chatbot', req.body);
        res.json(axiosResponse.data); 
    } catch (error) {
        console.error('Error with Python server:', error);
        res.status(500).json({ error: 'Error with Python server' });
    }
}

module.exports = { botController };