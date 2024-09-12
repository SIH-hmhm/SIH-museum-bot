import { React,useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Signup = () => {

    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!name || !password || !email || !confirmPassword) {
            return alert('Please fill in all fields');
        }

        try {
            const response = await axios.post('http://localhost:5000/api/users/signup', { name, email, password, confirmPassword }, {
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            const token = response.data.token;
            if (token) {
                localStorage.setItem('token', token);
                console.log('Token:', token);  // Log the token
                alert('Signup Successful');
                setName('');
                setEmail('');
                setPassword('');
                setConfirmPassword('');
                navigate('/');
            } else {
                alert('Signup failed: Token not received');
            }
        } catch (error) {
            console.error('Signup error:', error);
            alert(error.message);
        }
    };

    return(
        <div>
            <form onSubmit={handleSubmit}>
                <h2>Signup</h2>
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
        </div>
    );
};

export default Signup;


