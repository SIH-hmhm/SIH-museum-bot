import React, { useState } from 'react';
import axios from 'axios';
import {useNavigate} from 'react-router-dom';



const Login = ()=> {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();


    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!password || !email) {
            return alert('Please fill in all fields');
        }

        try {
            const response = await axios.post('http://localhost:5000/api/users/login', { email, password }, {
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            const token = response.data.token;
            if (token) {
                localStorage.setItem('token', token);
                console.log('Token:', token);  // Log the token
                alert('Login Successful');
                setEmail('');
                setPassword('');
                navigate('/');
            } else {
                alert('Login failed: Token not received');
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('An error occurred during login');
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <h2>Login</h2>
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
                <button type="submit">Login</button>
            </form>
        </div>
    );
}

export default Login;
