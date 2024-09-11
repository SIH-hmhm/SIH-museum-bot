import express from 'express';
import { signUp, login, logout } from '../Controller/userController.js';

const router = express.Router();

router.route('/signup').post(signUp);
router.route('/login').post(login);
router.route('/logout').get(logout);


export default router;