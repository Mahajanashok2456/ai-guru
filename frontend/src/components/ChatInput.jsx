import React from 'react';
import VoiceRecorder from './VoiceRecorder';

function ChatInput({
  value,
  onChange,
  onSubmit,
  onImageUpload,
  onVoiceToggle,
  onClear,
  isLoading,
  isConverting,
  isListening,
  speechSupported,
  speechInterimResult,
  speechError,
  fileInputRef,
}) {
  return (
    <div className="input-area">
      {/* Speech Recognition Error Display */}
      {speechError && (
        <div
          style={{
            backgroundColor: "#ffebee",
            border: "1px solid #f44336",
            borderRadius: "8px",
            padding: "12px 16px",
            margin: "0 0 16px 0",
            color: "#c62828",
            fontSize: "14px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <span>⚠️</span>
          <span>{speechError}</span>
          <button
            type="button"
            onClick={() => onChange("")}
            style={{
              marginLeft: "auto",
              background: "none",
              border: "none",
              color: "#c62828",
              cursor: "pointer",
              fontSize: "16px",
              padding: "4px",
            }}
            title="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}

      {/* Speech Recognition Status */}
      {isListening && (
        <div
          style={{
            backgroundColor: "#fff3e0",
            border: "1px solid #ff9800",
            borderRadius: "8px",
            padding: "12px 16px",
            margin: "0 0 16px 0",
            color: "#e65100",
            fontSize: "14px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            animation: "pulse 2s infinite",
          }}
        >
          <span>🎤</span>
          <span>
            Listening for speech... Speak clearly into your microphone.
          </span>
          <div
            style={{
              marginLeft: "auto",
              width: "12px",
              height: "12px",
              backgroundColor: "#ff4444",
              borderRadius: "50%",
              animation: "pulse 1s infinite",
            }}
          />
        </div>
      )}

      <form onSubmit={onSubmit}>
        <div 
          className="input-container"
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "#3C3D37";
            e.currentTarget.style.boxShadow =
              "0 8px 25px rgba(105, 117, 101, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.7)";
            e.currentTarget.style.transform = "translateY(-2px)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "#697565";
            e.currentTarget.style.boxShadow =
              "0 4px 20px rgba(105, 117, 101, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5)";
            e.currentTarget.style.transform = "translateY(0)";
          }}
        >
          {/* Attachment Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            style={{
              padding: "10px",
              backgroundColor: "transparent",
              border: "2px solid transparent",
              borderRadius: "50%",
              cursor: "pointer",
              color: "#697565",
              fontSize: "18px",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
              transform: "scale(1)",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = "rgba(105, 117, 101, 0.1)";
              e.target.style.borderColor = "#697565";
              e.target.style.transform = "scale(1.1) rotate(10deg)";
              e.target.style.boxShadow =
                "0 4px 12px rgba(105, 117, 101, 0.2)";
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = "transparent";
              e.target.style.borderColor = "transparent";
              e.target.style.transform = "scale(1) rotate(0deg)";
              e.target.style.boxShadow = "none";
            }}
            onMouseDown={(e) => {
              e.target.style.transform = "scale(0.95) rotate(5deg)";
            }}
            onMouseUp={(e) => {
              e.target.style.transform = "scale(1.05) rotate(-5deg)";
              setTimeout(() => {
                e.target.style.transform = "scale(1) rotate(0deg)";
              }, 200);
            }}
          >
            📎
          </button>
          {/* Text Input */}
          <input
            className="text-input"
            type="text"
            value={speechInterimResult || value}
            onChange={(e) =>
              !isConverting &&
              !isListening &&
              onChange(e.target.value)
            }
            placeholder={
              isListening
                ? "🎤 Listening... Speak now!"
                : isConverting
                ? "Converting voice to text..."
                : speechSupported
                ? "Type your message or click 🎤 for voice..."
                : "Type your message..."
            }
            style={{
              color: isListening
                ? "#ff4444"
                : isConverting
                ? "#697565"
                : speechInterimResult
                ? "#8B4513"
                : "#181C14",
              fontWeight: isListening ? "600" : "500",
              fontStyle:
                isConverting || isListening ? "italic" : "normal",
              opacity: speechInterimResult ? 0.8 : 1,
            }}
            disabled={isLoading || isConverting || isListening}
          />
          {/* Clear Transcription Button */}
          {value && !isConverting && (
            <button
              type="button"
              onClick={onClear}
              style={{
                padding: "8px",
                backgroundColor: "transparent",
                border: "2px solid #697565",
                borderRadius: "50%",
                cursor: "pointer",
                color: "#697565",
                fontSize: "14px",
                transition: "all 0.3s ease",
                marginLeft: "8px",
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = "#f0f0f0";
                e.target.style.borderColor = "#3C3D37";
                e.target.style.color = "#3C3D37";
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = "transparent";
                e.target.style.borderColor = "#697565";
                e.target.style.color = "#697565";
              }}
              title="Clear text"
            >
              ✕
            </button>
          )}

          {/* Voice Button */}
          <VoiceRecorder
            isListening={isListening}
            isLoading={isLoading}
            isConverting={isConverting}
            onToggle={onVoiceToggle}
            supported={speechSupported}
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={!value.trim() || isLoading || isConverting}
            style={{
              padding: "12px",
              backgroundColor:
                value.trim() && !isLoading && !isConverting
                  ? "#697565"
                  : "rgba(209, 213, 219, 0.6)",
              border:
                value.trim() && !isLoading && !isConverting
                  ? "2px solid #3C3D37"
                  : "2px solid transparent",
              borderRadius: "50%",
              cursor:
                value.trim() && !isLoading && !isConverting
                  ? "pointer"
                  : "not-allowed",
              color:
                value.trim() && !isLoading && !isConverting
                  ? "#ECDFCC"
                  : "#9ca3af",
              fontSize: "18px",
              fontWeight: "bold",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
              transform: "scale(1)",
              boxShadow:
                value.trim() && !isLoading && !isConverting
                  ? "0 4px 15px rgba(105, 117, 101, 0.4), 0 0 0 0 rgba(105, 117, 101, 0.7)"
                  : "0 2px 8px rgba(0, 0, 0, 0.1)",
              background:
                value.trim() && !isLoading && !isConverting
                  ? "linear-gradient(135deg, #697565 0%, #3C3D37 100%)"
                  : "rgba(209, 213, 219, 0.6)",
              animation:
                value.trim() && !isLoading && !isConverting
                  ? "pulse 2s infinite"
                  : "none",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseOver={(e) => {
              if (value.trim() && !isLoading && !isConverting) {
                e.target.style.transform = "scale(1.1)";
                e.target.style.background =
                  "linear-gradient(135deg, #3C3D37 0%, #181C14 100%)";
                e.target.style.boxShadow =
                  "0 8px 25px rgba(105, 117, 101, 0.6), 0 0 20px rgba(105, 117, 101, 0.4)";
                e.target.style.borderColor = "#ECDFCC";
              }
            }}
            onMouseOut={(e) => {
              if (value.trim() && !isLoading && !isConverting) {
                e.target.style.transform = "scale(1)";
                e.target.style.background =
                  "linear-gradient(135deg, #697565 0%, #3C3D37 100%)";
                e.target.style.boxShadow =
                  "0 4px 15px rgba(105, 117, 101, 0.4), 0 0 0 0 rgba(105, 117, 101, 0.7)";
                e.target.style.borderColor = "#3C3D37";
              }
            }}
            onMouseDown={(e) => {
              if (value.trim() && !isLoading && !isConverting) {
                e.target.style.transform = "scale(0.95)";
                e.target.style.animation = "none";
              }
            }}
            onMouseUp={(e) => {
              if (value.trim() && !isLoading && !isConverting) {
                e.target.style.transform = "scale(1.05)";
                e.target.style.animation = "sendPulse 0.6s ease-out";
                setTimeout(() => {
                  e.target.style.transform = "scale(1)";
                  e.target.style.animation = "pulse 2s infinite";
                }, 600);
              }
            }}
          >
            {isLoading ? (
              <div
                style={{
                  width: "18px",
                  height: "18px",
                  border: "2px solid transparent",
                  borderTop: "2px solid #ECDFCC",
                  borderRadius: "50%",
                  animation: "spin 1s linear infinite",
                }}
              ></div>
            ) : (
              "➤"
            )}
          </button>
        </div>
      </form>

      {/* Disclaimer */}
      <div
        style={{
          textAlign: "center",
          padding: "8px 5px",
          fontSize: "11px",
          color: "rgba(105, 117, 101, 0.7)",
          background: "transparent",
          borderTop: "1px solid rgba(105, 117, 101, 0.1)",
          fontWeight: "400",
          letterSpacing: "0.2px",
          lineHeight: "1.0",
        }}
      >
        AI Guru's got the brains, but it's still learning the ropes—verify
        important stuff, just in case!
      </div>
    </div>
  );
}

export default ChatInput;
