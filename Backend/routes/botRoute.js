import { Router } from 'express';
const router = Router();
import { botController } from '../Controller/botContoller.js';

router.post('/chatbot', botController);

export default router;
