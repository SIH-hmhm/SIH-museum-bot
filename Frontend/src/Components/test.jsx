import React, { useState } from 'react';
import { ENDPOINT_URL } from "../constant/constants"

const Chatbot = () => {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch(`${ENDPOINT_URL}/chatbot`, {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });
            const data = await res.json();
            setResponse(data.response);
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