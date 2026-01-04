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
      className={`action-btn ${isListening ? 'active' : ''}`}
      style={{
        background: isListening ? '#f43f5e' : 'transparent',
        color: isListening ? '#fff' : 'var(--text-muted)',
        border: isListening ? 'none' : '1px solid var(--glass-border)',
        boxShadow: isListening ? '0 0 20px rgba(244, 63, 94, 0.4)' : 'none',
        position: 'relative',
        transition: 'var(--transition)',
        marginRight: '4px'
      }}
      title={isListening ? "Stop listening" : "Voice input"}
    >
      {isListening ? (
        <span style={{ display: 'flex', gap: '2px' }}>
          <span className="dot" style={{ width: '4px', height: '4px', background: '#fff', borderRadius: '50%', animation: 'pulse 1s infinite' }}></span>
          <span className="dot" style={{ width: '4px', height: '4px', background: '#fff', borderRadius: '50%', animation: 'pulse 1s infinite 0.2s' }}></span>
          <span className="dot" style={{ width: '4px', height: '4px', background: '#fff', borderRadius: '50%', animation: 'pulse 1s infinite 0.4s' }}></span>
        </span>
      ) : "🎤"}
    </button>
  );
}

export default VoiceRecorder;
