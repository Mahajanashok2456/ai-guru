import { useState, useRef, useEffect } from 'react';
import { 
  sendChatMessage, 
  sendImageMessage, 
  fetchChatHistory, 
  deleteSessionById, 
  deleteAllHistory 
} from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [chatSessions, setChatSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentInput, setCurrentInput] = useState("");
  const [selectedImage, setSelectedImage] = useState(null);
  const [processingMessages, setProcessingMessages] = useState(new Set());

  const activeRequestsRef = useRef(new Map());
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Initial fetch of chat sessions
  useEffect(() => {
    refreshChatSessions();
  }, []);

  const refreshChatSessions = async () => {
    try {
      const sessions = await fetchChatHistory();
      setChatSessions(sessions);
    } catch (error) {
      console.error("Error fetching chat history:", error);
    }
  };

  const cancelActiveRequests = () => {
    activeRequestsRef.current.forEach((controller) => controller.abort());
    activeRequestsRef.current.clear();
    setIsLoading(false);
    setProcessingMessages(new Set());
  };

  const startNewChat = () => {
    cancelActiveRequests();
    setMessages([]);
    setSelectedSession(null);
    setCurrentSessionId(null);
    setCurrentInput("");
    setSelectedImage(null);
  };

  const deleteSession = async (sessionId) => {
    try {
      await deleteSessionById(sessionId);
      if (currentSessionId === sessionId) {
        startNewChat();
      }
      refreshChatSessions();
    } catch (error) {
      console.error("Error deleting session:", error);
    }
  };

  const deleteAllChatHistory = async () => {
    if (window.confirm("Are you sure you want to delete all chat history? This cannot be undone.")) {
      try {
        await deleteAllHistory();
        startNewChat();
        refreshChatSessions();
      } catch (error) {
        console.error("Error deleting all history:", error);
      }
    }
  };

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!currentInput.trim() || isLoading) return;

    const userMessage = currentInput.trim();
    setCurrentInput("");

    // Add user message to UI immediately
    const userMsgObj = {
      id: Date.now(),
      text: userMessage,
      sender: "user",
    };
    setMessages((prev) => [...prev, userMsgObj]);

    // Add AI placeholder message
    const aiPlaceholderId = Date.now() + 1;
    setMessages((prev) => [
      ...prev,
      { id: aiPlaceholderId, text: "", sender: "ai", isLoading: true },
    ]);

    setIsLoading(true);

    try {
      const controller = new AbortController();
      activeRequestsRef.current.set("chat", controller);

      const data = await sendChatMessage(userMessage, currentSessionId, controller.signal);

      // Store the session ID from the first message
      if (!currentSessionId && data.session_id) {
        setCurrentSessionId(data.session_id);
      }

      // Update AI message with response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiPlaceholderId
            ? {
                ...msg,
                text: data.response,
                isLoading: false,
                detectedLanguage: data.detected_language,
                languageName: data.language_name,
                confidence: data.confidence,
                sessionId: data.session_id,
                interactionId: data.interaction_id,
              }
            : msg
        )
      );

      // Refresh history in background
      refreshChatSessions();
    } catch (error) {
      if (error.name === "AbortError") return;
      
      console.error("Error sending message:", error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiPlaceholderId
            ? {
                ...msg,
                text: "⚠️ " + (error.message || "Something went wrong."),
                isLoading: false,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
      activeRequestsRef.current.delete("chat");
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Direct preview for UI
    const reader = new FileReader();
    reader.onload = async (event) => {
      const userMsgObj = {
        id: Date.now(),
        text: currentInput || "Analyze this image",
        sender: "user",
        image: event.target.result,
        imageName: file.name,
      };
      setMessages((prev) => [...prev, userMsgObj]);
      
      const aiPlaceholderId = Date.now() + 1;
      setMessages((prev) => [
        ...prev,
        { id: aiPlaceholderId, text: "", sender: "ai", isLoading: true },
      ]);

      setIsLoading(true);

      try {
        const controller = new AbortController();
        activeRequestsRef.current.set("image", controller);

        const data = await sendImageMessage(file, currentInput, currentSessionId, controller.signal);

        if (!currentSessionId && data.session_id) {
          setCurrentSessionId(data.session_id);
        }

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === aiPlaceholderId
              ? {
                  ...msg,
                  text: data.response,
                  isLoading: false,
                  detectedLanguage: data.detected_language,
                  languageName: data.language_name,
                  confidence: data.confidence,
                  sessionId: data.session_id,
                  interactionId: data.interaction_id,
                }
              : msg
          )
        );
        refreshChatSessions();
      } catch (error) {
        if (error.name === "AbortError") return;

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === aiPlaceholderId
              ? {
                  ...msg,
                  text: "⚠️ " + (error.message || "Failed to analyze image."),
                  isLoading: false,
                }
              : msg
          )
        );
      } finally {
        setIsLoading(false);
        activeRequestsRef.current.delete("image");
      }
    };
    reader.readAsDataURL(file);
    e.target.value = ""; // Reset input
  };

  const selectSession = (session) => {
    cancelActiveRequests();
    setSelectedSession(session);
    setCurrentSessionId(session.session_id);

    // Convert session messages to display format
    const displayMessages = [];
    session.messages.forEach((msg, index) => {
        // Add user message
        displayMessages.push({
            id: msg.id * 2 - 1,
            text: msg.user_input,
            sender: "user",
        });
        // Add AI response
        displayMessages.push({
            id: msg.id * 2,
            text: msg.bot_response,
            sender: "ai",
            detectedLanguage: msg.language_code,
            languageName: msg.language_name,
            sessionId: msg.session_id,
            interactionId: msg._id || `${msg.session_id}_${msg.id * 2}`,
        });
    });
    setMessages(displayMessages);
  };

  return {
    messages,
    setMessages,
    chatSessions,
    selectedSession,
    setSelectedSession,
    currentSessionId,
    setCurrentSessionId,
    isLoading,
    currentInput,
    setCurrentInput,
    selectedImage,
    processingMessages,
    messagesEndRef,
    activeRequestsRef,
    refreshChatSessions,
    startNewChat,
    handleSubmit,
    handleImageUpload,
    deleteSession,
    deleteAllChatHistory,
    selectSession
  };
};
