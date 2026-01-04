// API Service - Centralized API calls
// All fetch requests to the backend

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

console.log("🔌 Connected to Backend at:", API_BASE_URL);

// Chat API
export const sendChatMessage = async (message, sessionId, signal) => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
    }),
    signal: signal,
  });

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error("Server is busy (quota exceeded). Please wait a moment.");
    }
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// Image API
export const sendImageMessage = async (imageFile, text, sessionId, signal) => {
  const formData = new FormData();
  formData.append("image", imageFile);
  formData.append("text", text || "Describe this image in detail.");
  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  const response = await fetch(`${API_BASE_URL}/image-chat`, {
    method: "POST",
    body: formData,
    signal: signal,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// Voice API
export const sendVoiceMessage = async (audioBlob, sessionId, signal) => {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.wav");
  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  const response = await fetch(`${API_BASE_URL}/voice-chat`, {
    method: "POST",
    body: formData,
    signal: signal,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// Transcription API
export const transcribeAudio = async (audioBlob) => {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.wav");

  const response = await fetch(`${API_BASE_URL}/transcribe`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// History API
export const fetchChatHistory = async () => {
  const response = await fetch(`${API_BASE_URL}/chat-history`);
  const data = await response.json();
  return data.sessions || [];
};

export const deleteSessionById = async (sessionId) => {
  const response = await fetch(`${API_BASE_URL}/session/${sessionId}`, {
    method: "DELETE",
  });
  return await response.json();
};

export const deleteAllHistory = async () => {
  const response = await fetch(`${API_BASE_URL}/chat-history`, {
    method: "DELETE",
  });
  return await response.json();
};

// Feedback API
export const submitFeedbackToAPI = async (interactionId, sessionId, feedbackType, feedbackText = "") => {
  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      interaction_id: interactionId,
      session_id: sessionId,
      feedback_type: feedbackType,
      feedback_text: feedbackText,
    }),
  });

  return await response.json();
};
