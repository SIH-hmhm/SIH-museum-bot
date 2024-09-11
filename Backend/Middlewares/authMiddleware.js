import jwt from 'jsonwebtoken';
import User from '../models/userSchema.js';

// Protect routes from unauthorized users
export const protect = async (req, res, next) => {
    
    // Check if token is present in the request headers or cookies
    let token;
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        token = req.headers.authorization.split(' ')[1];
    } else if (req.cookies && req.cookies.token) {
        token = req.cookies.token;
    }
    // If token is not present, return an error message not authorized
    if (!token) {
        return res.status(401).json({ status: "fail", message: "Not authorized, no token" });
    }

    // Verify the token and decode it
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = await User.findById(decoded.id).select('-password');
        // If user is not found, return an error message not authorized
        next();
    } catch (error) {
        res.status(401).json({ status: "fail", message: "Not authorized, token failed" });
    }
};