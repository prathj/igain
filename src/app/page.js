'use client';
import Image from "next/image";
import styles from "./page.module.css";
import { useState, useEffect } from 'react';

export default function Home() {
  const [chatbotData, setChatbotData] = useState(null);
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch initial chatbot data from Flask backend
    fetch('http://localhost:5000/api/app')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setChatbotData(data);
        // Add greeting message to chat history
        setChatHistory([{ type: 'bot', content: data.greeting }]);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching chatbot data:', error);
        setError('Failed to load chatbot data. Please make sure your Flask server is running.');
        setLoading(false);
      });
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    
    // Add user message to chat history
    setChatHistory(prev => [...prev, { type: 'user', content: message }]);
    
    // Send message to Flask backend
    try {
      const response = await fetch('http://localhost:5000/api/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      
      // Add bot response to chat history
      setChatHistory(prev => [...prev, { type: 'bot', content: data.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prev => [...prev, { type: 'bot', content: 'Sorry, there was an error processing your request.' }]);
    }
    
    // Clear input field
    setMessage('');
  };

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <h1 className={styles.title}>iGain</h1>
        <p className={styles.subtext}>The #2 AI Knowledge Platform for Customer Service</p>
        
        {/* Chatbot Interface */}
        <div className={styles.chatbotContainer}>
          {loading ? (
            <p>Loading chatbot...</p>
          ) : error ? (
            <p className={styles.error}>{error}</p>
          ) : (
            <>
              <div className={styles.chatHistory}>
                {chatHistory.map((chat, index) => (
                  <div key={index} className={`${styles.chatMessage} ${styles[chat.type]}`}>
                    {chat.content}
                  </div>
                ))}
              </div>
              <form onSubmit={handleSendMessage} className={styles.chatForm}>
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type your message here..."
                  className={styles.chatInput}
                />
                <button type="submit" className={styles.sendButton}>Send</button>
              </form>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
