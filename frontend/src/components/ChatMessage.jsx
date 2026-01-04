import React from 'react';
import { marked } from 'marked';
import FeedbackButtons from './FeedbackButtons';

function ChatMessage({ message, index, onSubmitFeedback, feedbackLoading }) {
  const isUser = message.sender === "user";

  return (
    <div
      key={message.id || index}
      className={`message-row ${isUser ? 'user' : 'bot'} animate-fade-in-up`}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      {!isUser && (
        <div style={{
          width: "32px",
          height: "32px",
          borderRadius: "50%",
          background: "var(--brand-gradient)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginRight: "12px",
          marginTop: "4px",
          fontSize: "14px",
          boxShadow: "var(--shadow-glow)"
        }}>
          🤖
        </div>
      )}
      
      <div className={`message-content ${isUser ? 'user' : 'bot'}`}>
        {message.image && (
          <div style={{ marginBottom: "12px" }}>
            <img
              src={message.image}
              alt={message.imageName || "Uploaded image"}
              style={{
                maxWidth: "100%",
                borderRadius: "var(--radius-md)",
                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                cursor: "pointer",
                transition: "var(--transition)"
              }}
              onClick={() => window.open(message.image, "_blank")}
            />
          </div>
        )}

        {message.isLoading ? (
          <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--text-muted)" }}>
            <div className="animate-spin" style={{ width: "16px", height: "16px", border: "2px solid transparent", borderTopColor: "var(--brand-primary)", borderRadius: "50%" }}></div>
            <span style={{ fontSize: "0.9rem" }}>Guru is thinking...</span>
          </div>
        ) : (
          <>
            <div
              className="markdown-content"
              dangerouslySetInnerHTML={{
                __html: marked.parse(message.text || "", { breaks: true, gfm: true }),
              }}
              style={{
                fontSize: "0.95rem",
                color: isUser ? "#fff" : "var(--text-main)"
              }}
            />

            {!isUser && message.detectedLanguage && message.languageName !== "Unknown" && message.detectedLanguage !== "en" && (
              <div style={{
                marginTop: "12px",
                padding: "4px 10px",
                backgroundColor: "rgba(45, 212, 191, 0.1)",
                borderRadius: "var(--radius-full)",
                fontSize: "0.75rem",
                color: "var(--brand-secondary)",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                border: "1px solid rgba(45, 212, 191, 0.2)"
              }}>
                🌐 {message.languageName} {message.confidence && `(${Math.round(message.confidence * 100)}%)`}
              </div>
            )}

            {!isUser && message.interactionId && !message.feedbackSubmitted && (
              <FeedbackButtons
                interactionId={message.interactionId}
                sessionId={message.sessionId}
                onSubmitFeedback={onSubmitFeedback}
                isLoading={feedbackLoading.has(message.interactionId)}
              />
            )}

            {message.feedbackSubmitted && (
              <div style={{
                marginTop: "12px",
                fontSize: "0.75rem",
                color: "var(--brand-secondary)",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                opacity: 0.8
              }}>
                ✓ Thanks for your help!
              </div>
            )}
          </>
        )}
      </div>

      {isUser && (
        <div style={{
          width: "32px",
          height: "32px",
          borderRadius: "50%",
          background: "var(--bg-surface-light)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginLeft: "12px",
          marginTop: "4px",
          fontSize: "14px",
          border: "1px solid var(--glass-border)"
        }}>
          👤
        </div>
      )}
    </div>
  );
}

export default ChatMessage;
