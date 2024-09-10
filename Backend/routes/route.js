const express = require('express');
const router = express.Router();
const axios = require('axios');

router.post('/chatbot', async (req, res) => {
    try {
        const res = await axios.post('http://localhost:5001/chatbot', req.body);
        res.json(res.data);
    } catch (error) {
        res.status(500).json({ error: 'eror python server' });
    }
});

module.exports = router;