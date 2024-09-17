import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./css/form.css";

const Signup = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const navigate = useNavigate();


    const handleSubmit = async (event) => {
        event.preventDefault();
        
        setErrorMessage('');

        // Validation: Check for empty fields
        if (!name || !email || !password || !confirmPassword) {
            return setErrorMessage('Please fill in all fields');
        }

        // Validation: Check if passwords match
        if (password !== confirmPassword) {
            return setErrorMessage('Passwords do not match');
        }

        try {
            // Send POST request to signup API
            const response = await axios.post('http://localhost:5000/api/users/signup', { 
                name, email, password, confirmPassword 
            }, {
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            const token = response.data.token;

            // Handle success: Store token and redirect
            if (token) {
                localStorage.setItem('token', token);
                alert('Signup Successful');
                setName('');
                setEmail('');
                setPassword('');
                setConfirmPassword('');
                navigate('/');
            } else {
                setErrorMessage('Signup failed: Token not received');
            }
        } catch (error) {
            console.error('Signup error:', error);
            setErrorMessage(error.response?.data?.error || 'An error occurred during signup');
        }
    };

    // This function will be triggered when the user clicks the Google OAuth button
    const handleGoogleOAuth = () => {
        // Redirect to the backend endpoint that handles Google OAuth
        window.location.href = 'http://localhost:5000/api/users/google';
    };

    return (
        <div className="signup-form">
            <form onSubmit={handleSubmit}>
                <h2>Signup</h2>
                
                {errorMessage && <p className="error-message">{errorMessage}</p>}
                
                <input 
                    type="text" 
                    name="name" 
                    id="name" 
                    placeholder="Name" 
                    value={name} 
                    onChange={(e) => setName(e.target.value)} 
                />
                <input 
                    type="email" 
                    name="email" 
                    id="email" 
                    placeholder="Email" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                />
                <input 
                    type="password" 
                    name="password" 
                    id="password" 
                    placeholder="Password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                />
                <input 
                    type="password" 
                    name="confirmPassword" 
                    id="confirmPassword" 
                    placeholder="Confirm Password" 
                    value={confirmPassword} 
                    onChange={(e) => setConfirmPassword(e.target.value)} 
                />
                <button type="submit">Signup</button>
            </form>

            <div className="oauth-section">
                <button onClick={handleGoogleOAuth} className="google-oauth-button">
                    Signup with Google
                </button>
            </div>
        </div>
    );
};

export default Signup;
