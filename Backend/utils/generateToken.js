import jwt from 'jsonwebtoken';

// Generate JWT token


export const generateToken = (id, res) => {
    const token = jwt.sign({ id }, process.env.JWT_SECRET, {
        expiresIn: process.env.JWT_EXPIRES_IN,
    });

    // Store the token in the cookie for 30 days  
    res.cookie('token', token, {
        expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
        httpOnly: true,
    });

    return token;
};

export default generateToken;
