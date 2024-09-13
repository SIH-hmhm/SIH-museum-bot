import jwt from 'jsonwebtoken';
import User from '../Models/userModel.js';

// Protect routes from unauthorized users
export const protect = async (req, res, next) => {
    let token;

    // Check for token in headers
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        token = req.headers.authorization.split(' ')[1];
    } else if (req.cookies && req.cookies.token) {
        // Check for token in cookies
        token = req.cookies.token;
    }

    if (!token) {
        return res.status(401).json({ status: 'fail', message: 'Not authorized, no token' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = await User.findById(decoded.id).select('-password');
        next();
    } catch (error) {
        res.status(401).json({ status: 'fail', message: 'Not authorized, token failed' });
    }
};
