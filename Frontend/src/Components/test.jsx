import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Chatbot = () => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        const fetchChats = async () => {
            const token = localStorage.getItem('token');

            if (!token) {
                alert('Please log in first');
                return;
            }

            try {
                const res = await axios.get('http://localhost:5000/api/chatbot', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                console.log(res.data);

                // Process the chat history to include both user and bot messages
                const chatHistory = res.data.map(chat => ({
                    userText: chat.message,   // User's message
                    botText: chat.botReply,   // Bot's reply
                }));

                setMessages(chatHistory);
            } catch (error) {
                console.error('Error fetching chats:', error);
            }
        };

        fetchChats();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const token = localStorage.getItem('token');

        if (!token) {
            alert('Please log in first');
            return;
        }

        try {
            // Add the user's message to the messages state
            const userMessage = { userText: message };
            setMessages([...messages, userMessage]);

            // Send the message to the server
            const res = await axios.post('http://localhost:5000/api/chatbot', { message }, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });

            // Add the bot's response to the messages state
            const botMessage = { botText: res.data.response };
            setMessages([...messages, userMessage, botMessage]);

            // Clear the input field
            setMessage('');
        } catch (error) {
            console.error('Error with chatbot:', error);
        }
    };

    return (
        <div>
            <div>
                {messages.map((msg, index) => (
                    <div key={index}>
                        {msg.userText && (
                            <p className="user">
                                <strong>You:</strong> {msg.userText}
                            </p>
                        )}
                        {msg.botText && (
                            <p className="bot">
                                <strong>Chatbot:</strong> {msg.botText}
                            </p>
                        )}
                    </div>
                ))}
            </div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message"
                />
                <button type="submit">Send</button>
            </form>
        </div>
    );
};

export default Chatbot;
