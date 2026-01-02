import React, { useState, useEffect } from 'react';
import './index.css';


function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [stars, setStars] = useState([]);

  useEffect(() => {
    const generateStars = () => {
      const newStars = [];
      for (let i = 0; i < 75; i++) {
        newStars.push({
          id: i,
          left: Math.random() * 100 + '%',
          top: Math.random() * 100 + '%',
          animationDuration: Math.random() * 3 + 2 + 's',
          animationDelay: Math.random() * 2 + 's',
        });
      }
      setStars(newStars);
    };
    generateStars();
  }, []);

  // This is your local backend server
  // This is your local backend server, unless an environment variable is set
  const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
  const API_URL = `${BASE_URL}/chat`;
  const HEALTH_URL = `${BASE_URL}/health`;

  // Check if backend is running
  const checkBackendHealth = async () => {
    try {
      console.log('Checking backend health...');
      const response = await fetch(HEALTH_URL);
      console.log('Backend health check passed:', response.status);
      return true;
    } catch (error) {
      console.error('Backend health check failed:', error.message);
      return false;
    }
  };

  const sendMessage = async () => {
    const messageToSend = userInput.trim(); // Capture the input before clearing
    if (!messageToSend) return; // Don't send empty messages

    const newUserMessage = { sender: 'user', text: userInput };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setUserInput('');
    setIsLoading(true);

    try {
      // First check if backend is running
      const isHealthy = await checkBackendHealth();
      if (!isHealthy) {
        throw new Error('Backend server is not running. Please start the FastAPI server on port 8000.');
      }

      // Create the request body exactly as the backend expects
      const requestBody = {
        question: messageToSend // Use the captured input
      };

      console.log('DEBUG: Sending request to backend');
      console.log('URL:', API_URL);
      console.log('Method: POST');
      console.log('Headers:', {
        'Content-Type': 'application/json',
      });
      console.log('Request Body:', JSON.stringify(requestBody, null, 2));

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // This header is crucial!
        },
        body: JSON.stringify(requestBody), // Convert to JSON string
      });

      console.log('DEBUG: Response status:', response.status);
      console.log('DEBUG: Response status text:', response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('DEBUG: Error response body:', errorText);
        throw new Error(`HTTP ${response.status} ${response.statusText}: ${errorText}`);
      }

      const data = await response.json();
      
      // Add the bot's response
      const botMessage = { sender: 'bot', text: data.answer };
      setMessages(prevMessages => [...prevMessages, botMessage]);

    } catch (error) {
      console.error("Failed to send message:", error);

      let errorText = 'Sorry, something went wrong. Please try again.';
      if (error.message.includes('422')) {
        errorText = '422 Error: The request format is incorrect. Check the console for details.';
      } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorText = 'Network Error: Make sure the backend server is running on port 8000.';
      }

      const errorMessage = { sender: 'bot', text: errorText };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      sendMessage();
    }
  };

  return (
    <div className="app-wrapper">
      <div className="stars-container">
        {stars.map((star) => (
          <div
            key={star.id}
            className="star"
            style={{
              left: star.left,
              top: star.top,
              animationDuration: star.animationDuration,
              animationDelay: star.animationDelay,
            }}
          />
        ))}
      </div>
      
      <div className="chat-container">
        <div className="chat-header">
          <h2>Therapist</h2>
          <p>be free to ask me anything</p>
        </div>

        <div className="message-list">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.sender}`}>
              {msg.sender === 'bot' && (
                <div className="bot-avatar">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14h2v2h-2zm0-10h2c0 2-3 1.8-3 5h2c0-2.2 3-2.5 3-5 0-2.21-1.79-4-4-4S8 3.79 8 6h2c0-1.1.9-2 2-2z"/>
                  </svg>
                </div>
              )}
              <div className={`message ${msg.sender}`}>
                {msg.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-row bot">
              <div className="bot-avatar">
                <svg viewBox="0 0 24 24" fill="currentColor">
                   <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14h2v2h-2zm0-10h2c0 2-3 1.8-3 5h2c0-2.2 3-2.5 3-5 0-2.21-1.79-4-4-4S8 3.79 8 6h2c0-1.1.9-2 2-2z"/>
                </svg>
              </div>
              <div className="message bot">
                <div className="typing-indicator">
                  <span className="typing-dot">.</span>
                  <span className="typing-dot">.</span>
                  <span className="typing-dot">.</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input">
          <div className="input-wrapper">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask for guidance..."
              disabled={isLoading}
            />
            <button onClick={sendMessage} disabled={isLoading}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width: '20px', height: '20px'}}>
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;