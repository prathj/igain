'use client';
import Image from "next/image";
import styles from "./page.module.css";
import { useState, useEffect, useRef } from 'react';

export default function Home() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    // fetch initial chatbot data from FastAPI backend
    fetch('http://localhost:5328/api/chatbot-data')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // just add the greeting message to chat history
        setChatHistory([{ type: 'bot', content: data.greeting }]);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching chatbot data:', error);
        setError('Failed to load chatbot data. Please make sure your server is running.');
        setLoading(false);
      });
  }, []);

  // scroll to bottom when chat history updates
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    
    // add user message to chat history
    setChatHistory(prev => [...prev, { type: 'user', content: message }]);
    
    // send message to backend
    try {
      const response = await fetch('http://localhost:5328/api/send-message', {
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
      
      // add bot response to chat history
      setChatHistory(prev => [...prev, { type: 'bot', content: data.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prev => [...prev, { type: 'bot', content: 'Sorry, there was an error processing your request.' }]);
    }
    
    // clear input field
    setMessage('');
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // simplify the refresh function too
  const handleRefreshChat = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5328/api/chatbot-data');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      // reset chat history with just the greeting
      setChatHistory([{ type: 'bot', content: data.greeting }]);
    } catch (error) {
      console.error('Error refreshing chatbot:', error);
      setError('Failed to refresh the chatbot. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <h1 className={styles.title}>iGain</h1>
        <p className={styles.subtext}>The #2 AI Knowledge Platform for Customer Service</p>
        
        {/* main page content here */}
        <div className={styles.content}>
          <p>Our AI-powered chatbot can help you track you lost package!</p>
          <p>Click the chat icon in the bottom-right corner to get started.</p>
        </div>
      </main>
      
      {/* Chatbot Icon */}
      <div 
        className={styles.chatbotIcon} 
        onClick={toggleChat}
        title="Chat with iGain Assistant"
      >
        💬
      </div>
      
      {/* Chatbot Container */}
      <div className={`${styles.chatbotPopup} ${isOpen ? styles.open : ''}`}>
        <div className={styles.chatbotHeader}>
          <h3>iGain Assistant</h3>
          <div className={styles.headerButtons}>
            <button 
              className={styles.refreshButton} 
              onClick={handleRefreshChat} 
              aria-label="Refresh conversation"
              title="Refresh conversation"
            >
              ↻
            </button>
            <button 
              className={styles.closeButton} 
              onClick={toggleChat} 
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>
        </div>
        
        {/* Chatbot Interface */}
        <div className={styles.chatbotContainer}>
          {loading ? (
            <p className={styles.loadingText}>Loading chatbot...</p>
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
                <div ref={chatEndRef} />
              </div>
              <form onSubmit={handleSendMessage} className={styles.chatForm}>
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type your message here..."
                  className={styles.chatInput}
                />
                <button type="submit" className={styles.sendButton}>
                  →
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
