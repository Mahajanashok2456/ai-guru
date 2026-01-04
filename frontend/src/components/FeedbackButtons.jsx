import React from 'react';

function FeedbackButtons({ interactionId, sessionId, onSubmitFeedback, isLoading }) {
  return (
    <div
      style={{
        marginTop: "12px",
        display: "flex",
        gap: "8px",
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      <div
        style={{
          fontSize: "12px",
          color: "#6b7280",
          marginRight: "4px",
        }}
      >
        Was this helpful?
      </div>
      <button
        onClick={() =>
          onSubmitFeedback(
            interactionId,
            sessionId,
            "thumbs_up"
          )
        }
        disabled={isLoading}
        style={{
          background: "none",
          border: "1px solid #e5e7eb",
          borderRadius: "16px",
          padding: "4px 8px",
          cursor: "pointer",
          fontSize: "12px",
          color: "#6b7280",
          display: "flex",
          alignItems: "center",
          gap: "4px",
          transition: "all 0.2s",
          opacity: isLoading ? 0.6 : 1,
        }}
        onMouseOver={(e) => {
          e.target.style.backgroundColor = "#f3f4f6";
          e.target.style.borderColor = "#10b981";
          e.target.style.color = "#10b981";
        }}
        onMouseOut={(e) => {
          e.target.style.backgroundColor = "transparent";
          e.target.style.borderColor = "#e5e7eb";
          e.target.style.color = "#6b7280";
        }}
      >
        👍 Yes
      </button>
      <button
        onClick={() =>
          onSubmitFeedback(
            interactionId,
            sessionId,
            "thumbs_down"
          )
        }
        disabled={isLoading}
        style={{
          background: "none",
          border: "1px solid #e5e7eb",
          borderRadius: "16px",
          padding: "4px 8px",
          cursor: "pointer",
          fontSize: "12px",
          color: "#6b7280",
          display: "flex",
          alignItems: "center",
          gap: "4px",
          transition: "all 0.2s",
          opacity: isLoading ? 0.6 : 1,
        }}
        onMouseOver={(e) => {
          e.target.style.backgroundColor = "#fef2f2";
          e.target.style.borderColor = "#ef4444";
          e.target.style.color = "#ef4444";
        }}
        onMouseOut={(e) => {
          e.target.style.backgroundColor = "transparent";
          e.target.style.borderColor = "#e5e7eb";
          e.target.style.color = "#6b7280";
        }}
      >
        👎 No
      </button>
      <select
        onChange={(e) => {
          if (e.target.value) {
            onSubmitFeedback(
              interactionId,
              sessionId,
              e.target.value
            );
            e.target.value = "";
          }
        }}
        disabled={isLoading}
        style={{
          background: "none",
          border: "1px solid #e5e7eb",
          borderRadius: "16px",
          padding: "4px 8px",
          cursor: "pointer",
          fontSize: "12px",
          color: "#6b7280",
          opacity: isLoading ? 0.6 : 1,
        }}
      >
        <option value="">Issues?</option>
        <option value="format_mismatch">Wrong format</option>
        <option value="too_long">Too long</option>
        <option value="too_short">Too short</option>
        <option value="off_topic">Off topic</option>
      </select>
    </div>
  );
}

export default FeedbackButtons;
