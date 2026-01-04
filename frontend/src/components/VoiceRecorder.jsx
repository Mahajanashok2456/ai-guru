import React from 'react';

function VoiceRecorder({ 
  isListening, 
  isLoading, 
  isConverting, 
  onToggle, 
  supported 
}) {
  if (!supported) return null;

  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={isLoading || isConverting}
      style={{
        padding: "12px",
        backgroundColor: isListening ? "#ff4444" : "#8B4513",
        border: isListening
          ? "2px solid #ff6666"
          : "2px solid #A0522D",
        borderRadius: "50%",
        cursor:
          isLoading || isConverting ? "not-allowed" : "pointer",
        color: "white",
        fontSize: "18px",
        fontWeight: "bold",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        transform: "scale(1)",
        boxShadow: isListening
          ? "0 4px 15px rgba(255, 68, 68, 0.4), 0 0 20px rgba(255, 68, 68, 0.3)"
          : "0 4px 15px rgba(139, 69, 19, 0.4)",
        background: isListening
          ? "linear-gradient(135deg, #ff4444 0%, #cc0000 100%)"
          : "linear-gradient(135deg, #8B4513 0%, #654321 100%)",
        animation: isListening ? "pulse 1.5s infinite" : "none",
        marginRight: "8px",
        opacity: isLoading || isConverting ? 0.6 : 1,
      }}
      onMouseOver={(e) => {
        if (!isLoading && !isConverting) {
          e.target.style.transform = "scale(1.1)";
          e.target.style.boxShadow = isListening
            ? "0 8px 25px rgba(255, 68, 68, 0.6), 0 0 30px rgba(255, 68, 68, 0.4)"
            : "0 8px 25px rgba(139, 69, 19, 0.6), 0 0 20px rgba(139, 69, 19, 0.4)";
        }
      }}
      onMouseOut={(e) => {
        if (!isLoading && !isConverting) {
          e.target.style.transform = "scale(1)";
          e.target.style.boxShadow = isListening
            ? "0 4px 15px rgba(255, 68, 68, 0.4), 0 0 20px rgba(255, 68, 68, 0.3)"
            : "0 4px 15px rgba(139, 69, 19, 0.4)";
        }
      }}
      title={
        isListening
          ? "Click to stop voice input"
          : "Click to start voice input"
      }
    >
      {isListening ? "🛑" : "🎤"}
    </button>
  );
}

export default VoiceRecorder;
