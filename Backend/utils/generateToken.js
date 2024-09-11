import jwt from 'jsonwebtoken';

// Generate JWT token
// This function generates a JWT token for the user and stores it in the cookie for 30 days and returns the token to the user for further use. 
export const generateToken = (id,res) => {
    // Generate JWT token for the user with the user id and the secret key and the expiry time of the token 
  const token = jwt.sign({ id }, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRES_IN,
  });

  // Store the token in the cookie for 30 days  
  res.cookie('token', token, {
    expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    httpOnly: true,
  });

    return token;

 
}

export default generateToken;
