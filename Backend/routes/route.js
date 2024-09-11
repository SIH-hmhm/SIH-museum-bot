const express = require('express');
const router = express.Router();
const  bot = require('../Controller/botContoller');

router.post('/chatbot', bot.botController);

module.exports = router;
