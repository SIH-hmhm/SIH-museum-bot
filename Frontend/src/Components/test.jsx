import React, { useState } from 'react';
import axios from 'axios';

const Chatbot = () => {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post('http://localhost:5000/api/chatbot', { message }, {
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            setResponse(res.data.response);
        } catch (error) {
            console.error('Error with chatbot:', error);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message"
                />
                <button type="submit">Send</button>
            </form>
            {response && <p>Chatbot: {response}</p>}
        </div>
    );
};

export default Chatbot;
