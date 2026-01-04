import React from 'react';
import ChatMessage from './ChatMessage';

function ChatWindow({
  messages,
  selectedSession,
  isLoading,
  onSubmitFeedback,
  feedbackLoading,
  onSuggestionClick,
  onImageUpload,
  messagesEndRef,
  fileInputRef,
}) {
  return (
    <div className="chat-window">
      <div className="messages-container">
        {/* Welcome Screen */}
        {!selectedSession && messages.length === 0 && (
          <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "100%",
            textAlign: "center",
            padding: "60px 20px",
            animation: "fadeInUp 0.8s ease-out"
          }}>
            <div style={{
              width: "80px",
              height: "80px",
              background: "var(--brand-gradient)",
              borderRadius: "24px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "40px",
              marginBottom: "32px",
              boxShadow: "var(--shadow-glow)",
              transform: "rotate(-10deg)"
            }}>
              🤖
            </div>
            
            <h1 className="welcome-title" style={{
              fontSize: "2.5rem",
              fontWeight: "700",
              color: "var(--text-main)",
              marginBottom: "16px",
              letterSpacing: "-1px"
            }}>
              How can I help you today?
            </h1>
            
            <p className="welcome-text" style={{
              fontSize: "1.1rem",
              color: "var(--text-muted)",
              marginBottom: "40px",
              maxWidth: "520px",
              lineHeight: "1.6"
            }}>
              Your companion for intelligent conversations, voice interactions, and visual analysis.
            </p>

            <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", justifyContent: "center" }}>
              {[
                { label: "Analyze an Image", icon: "🖼️", action: () => fileInputRef.current?.click() },
                { label: "Brainstorm Ideas", icon: "💡", action: () => onSuggestionClick("I need some creative ideas for...") },
                { label: "Code Assistant", icon: "💻", action: () => onSuggestionClick("Can you help me with a coding problem?") }
              ].map((item, i) => (
                <button
                  key={i}
                  onClick={item.action}
                  style={{
                    padding: "16px 24px",
                    background: "var(--bg-surface-light)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "var(--radius-lg)",
                    color: "var(--text-main)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    transition: "var(--transition)",
                    fontSize: "0.95rem",
                    fontWeight: "500"
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = "translateY(-4px)";
                    e.currentTarget.style.borderColor = "var(--brand-primary)";
                    e.currentTarget.style.background = "rgba(129, 140, 248, 0.1)";
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.borderColor = "var(--glass-border)";
                    e.currentTarget.style.background = "var(--bg-surface-light)";
                  }}
                >
                  <span>{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat Messages */}
        <div style={{ width: "100%", maxWidth: "800px", margin: "0 auto" }}>
          {messages.map((msg, index) => (
            <ChatMessage
              key={msg.id || index}
              message={msg}
              index={index}
              onSubmitFeedback={onSubmitFeedback}
              feedbackLoading={feedbackLoading}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;
