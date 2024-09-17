import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './css/chat.css';

const Chatbot = () => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        const fetchChats = async () => {

            const urlParams = new URLSearchParams(window.location.search);
            const urlToken = urlParams.get('token');

            if (urlToken) {
                // Save token to local storage and log it
                localStorage.setItem('token', urlToken);
                console.log('Token:', urlToken);
            }

            const token = localStorage.getItem('token');

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
            <div className='chat-container'>
                <div className='Chat'>
                    {messages.map((msg, index) => (
                        <div key={index}>
                            {msg.userText && (
                                <p className="user">
                                    {msg.userText}
                                </p>
                            )}
                            {msg.botText && (
                                <p className="bot">
                                    {msg.botText}
                                </p>
                            )}
                        </div>
                    ))}
                </div>
            </div>
            <form onSubmit={handleSubmit} className='chat-form'>
                <div className='input-container'>
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Type your message"
                    />
                    <button type="submit" className="send-btn">&#10148;</button> {/* Unicode arrow */}
                </div>
            </form>

        </div>
    );
};

export default Chatbot;
