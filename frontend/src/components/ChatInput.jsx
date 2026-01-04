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
      {speechError && (
        <div style={{
          background: "rgba(239, 68, 68, 0.1)",
          border: "1px solid rgba(239, 68, 68, 0.2)",
          borderRadius: "var(--radius-md)",
          padding: "10px 16px",
          marginBottom: "16px",
          color: "#f87171",
          fontSize: "0.85rem",
          display: "flex",
          alignItems: "center",
          gap: "10px"
        }}>
          <span>⚠️</span>
          <span style={{ flex: 1 }}>{speechError}</span>
          <button onClick={() => onChange("")} style={{ background: "transparent", border: "none", color: "#f87171", cursor: "pointer" }}>✕</button>
        </div>
      )}

      <form onSubmit={onSubmit}>
        <div className="input-container">
          <button
            type="button"
            className="action-btn"
            onClick={() => fileInputRef.current?.click()}
            title="Attach image"
          >
            📎
          </button>

          <input
            className="text-input"
            type="text"
            value={speechInterimResult || value}
            onChange={(e) => !isConverting && !isListening && onChange(e.target.value)}
            placeholder={isListening ? "Listening..." : "Message Guru..."}
            disabled={isLoading || isConverting || isListening}
          />

          {value && !isConverting && (
            <button type="button" className="action-btn" onClick={onClear} title="Clear">
              ✕
            </button>
          )}

          <VoiceRecorder
            isListening={isListening}
            isLoading={isLoading}
            isConverting={isConverting}
            onToggle={onVoiceToggle}
            supported={speechSupported}
          />

          <button
            type="submit"
            className="action-btn send-btn"
            disabled={!value.trim() || isLoading || isConverting}
          >
            {isLoading ? "..." : "➤"}
          </button>
        </div>
      </form>

      <div style={{
        textAlign: "center",
        marginTop: "12px",
        fontSize: "0.7rem",
        color: "var(--text-dim)",
        opacity: 0.6
      }}>
        Guru may display inaccurate info. Verify important details.
      </div>
    </div>
  );
}

export default ChatInput;
