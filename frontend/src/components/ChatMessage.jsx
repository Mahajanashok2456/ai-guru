import React from 'react';
import { marked } from 'marked';
import FeedbackButtons from './FeedbackButtons';

function ChatMessage({ message, index, onSubmitFeedback, feedbackLoading }) {
  return (
    <div
      key={message.id || index}
      className="message-enter"
      style={{
        marginBottom: "24px",
        display: "flex",
        alignItems: "flex-start",
        gap: "16px",
        animationDelay: `${index * 0.1}s`,
      }}
    >
      <div
        style={{
          width: "40px",
          height: "40px",
          borderRadius: "50%",
          background:
            message.sender === "user"
              ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
              : "linear-gradient(135deg, #10b981, #06b6d4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          fontSize: "16px",
          fontWeight: "700",
          flexShrink: 0,
          boxShadow:
            message.sender === "user"
              ? "0 4px 12px rgba(99, 102, 241, 0.3)"
              : "0 4px 12px rgba(16, 185, 129, 0.3)",
          border: "2px solid rgba(255, 255, 255, 0.2)",
        }}
      >
        {message.sender === "user" ? "👤" : "🤖"}
      </div>
      <div
        style={{
          flex: 1,
          padding: "12px 16px",
          backgroundColor:
            message.sender === "user" ? "#f1f5f9" : "#f0fdf4",
          borderRadius: "12px",
          color: "#374151",
          fontSize: "14px",
          lineHeight: "1.5",
        }}
      >
        {message.image && (
          <div style={{ marginBottom: "12px" }}>
            <img
              src={message.image}
              alt={message.imageName || "Uploaded image"}
              style={{
                maxWidth: "300px",
                maxHeight: "200px",
                width: "100%",
                height: "auto",
                borderRadius: "8px",
                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
                cursor: "pointer",
                transition: "transform 0.2s ease",
              }}
              onMouseOver={(e) => {
                e.target.style.transform = "scale(1.02)";
              }}
              onMouseOut={(e) => {
                e.target.style.transform = "scale(1)";
              }}
              onClick={() => {
                window.open(message.image, "_blank");
              }}
            />
            <div
              style={{
                fontSize: "12px",
                color: "#6b7280",
                marginTop: "4px",
                fontStyle: "italic",
              }}
            >
              📷 {message.imageName}
            </div>
          </div>
        )}
        {message.isLoading ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              color: "#697565",
            }}
          >
            <div className="spinner"></div>
            <span>AI is thinking...</span>
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        ) : (
          <>
            <div
              dangerouslySetInnerHTML={{
                __html: marked.parse(message.text || "", {
                  breaks: true,
                  gfm: true,
                }),
              }}
              style={{
                lineHeight: "1.6",
                "& h1, & h2, & h3, & h4, & h5, & h6": {
                  marginTop: "16px",
                  marginBottom: "8px",
                  fontWeight: "bold",
                },
                "& p": {
                  marginBottom: "12px",
                },
                "& ul, & ol": {
                  marginLeft: "20px",
                  marginBottom: "12px",
                },
                "& li": {
                  marginBottom: "4px",
                },
                "& strong": {
                  fontWeight: "bold",
                  color: "#374151",
                },
                "& em": {
                  fontStyle: "italic",
                },
              }}
            />
            {/* Language Detection Indicator for AI messages */}
            {message.sender === "ai" &&
              message.detectedLanguage &&
              message.languageName &&
              message.languageName !== "Unknown" &&
              message.detectedLanguage !== "en" && (
                <div
                  style={{
                    marginTop: "8px",
                    padding: "6px 10px",
                    backgroundColor: "rgba(16, 185, 129, 0.1)",
                    borderRadius: "16px",
                    fontSize: "12px",
                    color: "#059669",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                    border: "1px solid rgba(16, 185, 129, 0.2)",
                  }}
                >
                  🌐 {message.languageName}{" "}
                  {message.confidence &&
                    `(${Math.round(message.confidence * 100)}%)`}
                </div>
              )}

            {/* Feedback Buttons for AI messages */}
            {message.sender === "ai" &&
              message.interactionId &&
              !message.feedbackSubmitted && (
                <FeedbackButtons
                  interactionId={message.interactionId}
                  sessionId={message.sessionId}
                  onSubmitFeedback={onSubmitFeedback}
                  isLoading={feedbackLoading.has(message.interactionId)}
                />
              )}

            {/* Feedback Confirmation Message */}
            {message.sender === "ai" && message.feedbackSubmitted && (
              <div
                style={{
                  marginTop: "8px",
                  padding: "8px 12px",
                  backgroundColor: "#f0f9ff",
                  borderRadius: "16px",
                  fontSize: "12px",
                  color: "#0369a1",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  border: "1px solid #0ea5e9",
                }}
              >
                <span>✓</span>
                <span>
                  Thanks! The AI learned from your{" "}
                  {message.feedbackSubmitted.replace("_", " ")}{" "}
                  feedback.
                </span>
              </div>
            )}

            {/* Dynamic Feedback Message */}
            {message.sender === "ai" && message.feedbackMessage && (
              <div
                style={{
                  marginTop: "8px",
                  padding: "8px 12px",
                  backgroundColor: "#f0fdf4",
                  borderRadius: "16px",
                  fontSize: "12px",
                  color: "#15803d",
                  border: "1px solid #22c55e",
                }}
              >
                {message.feedbackMessage}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
