import { Router } from 'express';
const router = Router();
import { botController, getChats } from '../Controller/botContoller.js';
import { protect } from '../Middlewares/authMiddleware.js';


router.post('/chatbot', protect ,botController);
router.get('/chatbot', protect ,getChats);

export default router;
