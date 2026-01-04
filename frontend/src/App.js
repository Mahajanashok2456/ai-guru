import React, { useState, useRef } from "react";

// Components
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import ImageUploader from './components/ImageUploader';

// Hooks
import { useChat } from './hooks/useChat';
import { useVoice } from './hooks/useVoice';
import { useFeedback } from './hooks/useFeedback';

function App() {
  const fileInputRef = useRef(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const {
    messages,
    setMessages,
    chatSessions,
    selectedSession,
    currentSessionId,
    isLoading,
    currentInput,
    setCurrentInput,
    messagesEndRef,
    activeRequestsRef,
    startNewChat,
    handleSubmit,
    handleImageUpload,
    deleteSession,
    deleteAllChatHistory,
    selectSession
  } = useChat();

  const {
    speechSupported,
    isListening,
    speechInterimResult,
    speechError,
    isRecording,
    isConverting,
    handleVoiceInput,
    clearTranscription
  } = useVoice(setCurrentInput, handleSubmit, currentSessionId, activeRequestsRef);

  const {
    feedbackLoading,
    submitFeedback
  } = useFeedback(setMessages);

  return (
    <>
      {/* CSS Animations */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
        }
        
        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
          }
          30% {
            transform: translateY(-10px);
          }
        }
        
        @keyframes glow {
          0%, 100% {
            box-shadow: 0 0 5px rgba(99, 102, 241, 0.3);
          }
          50% {
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.6);
          }
        }
        
        @keyframes shimmer {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }
        
        .message-enter {
          animation: fadeInUp 0.3s ease-out;
        }
        
        .sidebar-item:hover {
          transform: translateX(4px);
          transition: all 0.2s ease;
        }
        
        .typing-indicator {
          display: inline-flex;
          gap: 3px;
        }
        
        .typing-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #6b7280;
          animation: typing 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) {
          animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
          animation-delay: 0.4s;
        }
        
        .gradient-bg {
          background: linear-gradient(-45deg, #6366f1, #8b5cf6, #06b6d4, #10b981);
          background-size: 400% 400%;
          animation: gradient 3s ease infinite;
        }
        
        @keyframes gradient {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        
        .button-hover {
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .button-hover:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .spinner {
          border: 2px solid #f3f3f3;
          border-top: 2px solid #6366f1;
          border-radius: 50%;
          width: 16px;
          height: 16px;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes sendPulse {
          0% { 
            transform: scale(0.95); 
            box-shadow: 0 0 0 0 rgba(105, 117, 101, 0.7); 
          }
          50% { 
            transform: scale(1.1); 
            box-shadow: 0 0 0 15px rgba(105, 117, 101, 0.2); 
          }
          100% { 
            transform: scale(1); 
            box-shadow: 0 0 0 25px rgba(105, 117, 101, 0); 
          }
        }
        
        @keyframes buttonGlow {
          0% { 
            box-shadow: 0 4px 15px rgba(105, 117, 101, 0.4);
          }
          50% { 
            box-shadow: 0 6px 20px rgba(105, 117, 101, 0.6), 0 0 15px rgba(105, 117, 101, 0.3);
          }
          100% { 
            box-shadow: 0 4px 15px rgba(105, 117, 101, 0.4);
          }
        }
        
        @keyframes inputFocus {
          0% { 
            transform: translateY(0) scale(1);
            box-shadow: 0 4px 20px rgba(105, 117, 101, 0.1);
          }
          50% { 
            transform: translateY(-1px) scale(1.01);
            box-shadow: 0 8px 25px rgba(105, 117, 101, 0.2);
          }
          100% { 
            transform: translateY(0) scale(1);
            box-shadow: 0 6px 22px rgba(105, 117, 101, 0.15);
          }
        }
        
        @keyframes messageSlideIn {
          0% { 
            opacity: 0;
            transform: translateY(20px) scale(0.95);
          }
          100% { 
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>

      <div className="app-container">
      {/* Mobile Menu Button */}
      <button 
        className="mobile-menu-btn"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        aria-label="Toggle Menu"
      >
        {mobileMenuOpen ? "✕" : "☰"}
      </button>

      {/* Overlay for mobile sidebar */}
      {mobileMenuOpen && (
        <div 
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.4)',
            zIndex: 90,
            backdropFilter: 'blur(2px)'
          }}
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <Sidebar
        collapsed={sidebarCollapsed}
        mobileOpen={mobileMenuOpen}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        sessions={chatSessions}
        selectedSession={selectedSession}
        onSelectSession={(session) => {
          selectSession(session);
          setMobileMenuOpen(false); // Close menu on mobile after selection
        }}
        onDeleteSession={deleteSession}
        onDeleteAll={deleteAllChatHistory}
        onNewChat={() => {
          startNewChat();
          setMobileMenuOpen(false); // Close menu on mobile
        }}
      />

      <div className="main-content">
        <header className="header-top">
          <div className="creator-badge">
            Created by <a href="https://mahajanashok.vercel.app/" target="_blank" rel="noopener noreferrer">Mahajan Ashok</a>
          </div>
        </header>

        <ChatWindow
          messages={messages}
          selectedSession={selectedSession}
          isLoading={isLoading}
          onSubmitFeedback={submitFeedback}
          feedbackLoading={feedbackLoading}
          onSuggestionClick={(text) => setCurrentInput(text)}
          onImageUpload={() => fileInputRef.current?.click()}
          messagesEndRef={messagesEndRef}
          fileInputRef={fileInputRef}
        />

        <ChatInput
          value={currentInput}
          onChange={setCurrentInput}
          onSubmit={handleSubmit}
          onImageUpload={() => fileInputRef.current?.click()}
          onVoiceToggle={handleVoiceInput}
          onClear={clearTranscription}
          isLoading={isLoading}
          isConverting={isConverting}
          isListening={isListening}
          speechSupported={speechSupported}
          speechInterimResult={speechInterimResult}
          speechError={speechError}
          fileInputRef={fileInputRef}
        />

        <ImageUploader
          onUpload={handleImageUpload}
          fileInputRef={fileInputRef}
        />

        <footer className="footer-bottom">
          <p>© 2026 AI Guru Multibot | Built by <a href="https://mahajanashok.vercel.app/" target="_blank" rel="noopener noreferrer">Mahajan Ashok</a></p>
        </footer>
      </div>
    </div>
    </>
  );
}

export default App;
