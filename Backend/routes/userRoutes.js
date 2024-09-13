import express from 'express';
import { signUp, login, logout } from '../Controller/userController.js';
import passport from 'passport';
import generateToken from '../utils/generateToken.js';

const router = express.Router();

// User auth routes
router.route('/signup').post(signUp);
router.route('/login').post(login);
router.route('/logout').get(logout);

// Google auth route to initiate login
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

// Google auth callback route
router.get('/google/callback', 
    passport.authenticate('google', { failureRedirect: '/login' }),
    (req, res) => {
        // Successful authentication
        const token = generateToken(req.user._id, res);
        // Redirect with the token included in the URL
        res.redirect(`http://localhost:5002/?token=${token}`);
    }
);




export default router;
