import React, { useState, useRef, useEffect } from "react";

function App() {
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedHistory, setSelectedHistory] = useState(null);
  // Fetch chat history on mount
  useEffect(() => {
    fetch("http://localhost:5000/chat-history")
      .then((res) => res.json())
      .then((data) => {
        setChatHistory(data.history || []);
      })
      .catch((err) => {
        console.error("Failed to fetch chat history:", err);
      });
  }, []);
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!currentInput.trim()) return;

    const userInput = currentInput.trim();
    const userMessage = { text: userInput, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setCurrentInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userInput }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const aiMessage = { text: data.response, sender: "ai" };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = { text: `Error: ${error.message}`, sender: "error" };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/wav",
        });
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");

        setIsLoading(true);
        const userMessage = { text: "[Voice message]", sender: "user" };
        setMessages((prev) => [...prev, userMessage]);

        try {
          const response = await fetch("http://localhost:5000/voice-chat", {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          const aiMessage = { text: data.response, sender: "ai" };
          setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
          const errorMessage = {
            text: `Error: ${error.message}`,
            sender: "error",
          };
          setMessages((prev) => [...prev, errorMessage]);
        } finally {
          setIsLoading(false);

          // Stop tracks
          stream.getTracks().forEach((track) => track.stop());
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error starting recording:", error);
      const errorMessage = {
        text: `Error starting recording: ${error.message}`,
        sender: "error",
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "20px",
        display: "flex",
      }}
    >
      {/* Sidebar */}
      <div
        style={{
          width: "300px",
          borderRight: "1px solid #ccc",
          paddingRight: "20px",
          height: "80vh",
          overflowY: "auto",
        }}
      >
        <h3>Chat History</h3>
        {chatHistory.length === 0 ? (
          <div style={{ color: "#888" }}>No history yet.</div>
        ) : (
          chatHistory.map((entry) => (
            <div
              key={entry.id}
              onClick={() => setSelectedHistory(entry)}
              style={{
                padding: "10px",
                marginBottom: "8px",
                borderRadius: "8px",
                background:
                  selectedHistory && selectedHistory.id === entry.id
                    ? "#e3f2fd"
                    : "#f8f9fa",
                cursor: "pointer",
                boxShadow:
                  selectedHistory && selectedHistory.id === entry.id
                    ? "0 0 4px #1976d2"
                    : "none",
              }}
            >
              <div style={{ fontSize: "12px", color: "#555" }}>
                {new Date(entry.timestamp).toLocaleString()}
              </div>
              <div style={{ fontWeight: "bold", margin: "4px 0" }}>
                {entry.input_type === "text" && "💬"}
                {entry.input_type === "voice" && "🎤"}
                {entry.input_type === "image" && "📷"}
                {entry.input_type.charAt(0).toUpperCase() +
                  entry.input_type.slice(1)}
              </div>
              <div
                style={{
                  fontSize: "13px",
                  color: "#333",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {entry.user_input}
              </div>
            </div>
          ))
        )}
      </div>
      {/* Main chat area */}
      <div
        style={{
          flex: 1,
          paddingLeft: "20px",
          height: "80vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            border: "1px solid #ccc",
            padding: "10px",
            marginBottom: "10px",
          }}
        >
          {/* If a history entry is selected, show its details */}
          {selectedHistory ? (
            <div
              style={{
                marginBottom: "20px",
                background: "#f1f8e9",
                padding: "10px",
                borderRadius: "8px",
              }}
            >
              <div style={{ fontSize: "12px", color: "#555" }}>
                {new Date(selectedHistory.timestamp).toLocaleString()}
              </div>
              <div style={{ fontWeight: "bold", margin: "4px 0" }}>
                {selectedHistory.input_type === "text" && "💬"}
                {selectedHistory.input_type === "voice" && "🎤"}
                {selectedHistory.input_type === "image" && "📷"}
                {selectedHistory.input_type.charAt(0).toUpperCase() +
                  selectedHistory.input_type.slice(1)}
              </div>
              <div style={{ margin: "6px 0" }}>
                <strong>User:</strong> {selectedHistory.user_input}
              </div>
              <div style={{ margin: "6px 0" }}>
                <strong>Bot:</strong> {selectedHistory.bot_response}
              </div>
              <button
                style={{
                  marginTop: "8px",
                  padding: "6px 12px",
                  borderRadius: "6px",
                  background: "#1976d2",
                  color: "white",
                  border: "none",
                  cursor: "pointer",
                }}
                onClick={() => setSelectedHistory(null)}
              >
                Close
              </button>
            </div>
          ) : null}
          {/* Existing chat messages */}
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                margin: "10px 0",
                padding: "10px",
                borderRadius: "10px",
                textAlign: msg.sender === "user" ? "right" : "left",
                backgroundColor:
                  msg.sender === "user"
                    ? "#007bff"
                    : msg.sender === "error"
                    ? "#dc3545"
                    : "#f8f9fa",
                color:
                  msg.sender === "user" || msg.sender === "error"
                    ? "white"
                    : "black",
                marginLeft: msg.sender === "user" ? "20%" : "0",
                marginRight: msg.sender === "user" ? "0" : "20%",
              }}
            >
              {msg.text}
            </div>
          ))}
          {isLoading && (
            <div
              style={{
                margin: "10px 0",
                padding: "10px",
                borderRadius: "10px",
                textAlign: "left",
                backgroundColor: "#f8f9fa",
                color: "black",
                marginLeft: "0",
                marginRight: "20%",
              }}
            >
              AI is thinking...
            </div>
          )}
        </div>
        <form onSubmit={handleSubmit} style={{ display: "flex" }}>
          <input
            type="text"
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            placeholder="Type your message..."
            style={{ flex: 1, padding: "10px", border: "1px solid #ccc" }}
            disabled={isLoading || isRecording}
          />
          <button
            type="submit"
            disabled={isLoading || isRecording}
            style={{
              padding: "10px 20px",
              backgroundColor: isLoading || isRecording ? "#6c757d" : "#007bff",
              color: "white",
              border: "none",
              cursor: isLoading || isRecording ? "not-allowed" : "pointer",
            }}
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
          <button
            type="button"
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isLoading}
            style={{
              padding: "10px 20px",
              backgroundColor: isRecording ? "#dc3545" : "#28a745",
              color: "white",
              border: "none",
              cursor: isLoading ? "not-allowed" : "pointer",
              marginLeft: "10px",
            }}
          >
            {isRecording ? "Stop" : "🎤"}
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={(e) => setSelectedImage(e.target.files[0])}
            style={{ display: "none" }}
          />

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isRecording}
            style={{
              padding: "10px 20px",
              backgroundColor: isLoading || isRecording ? "#6c757d" : "#17a2b8",
              color: "white",
              border: "none",
              cursor: isLoading || isRecording ? "not-allowed" : "pointer",
              marginLeft: "10px",
            }}
          >
            📷
          </button>

          {selectedImage && (
            <button
              type="button"
              onClick={async () => {
                if (!selectedImage) return;
                setIsLoading(true);
                const prompt = currentInput.trim() || "Describe this image.";
                const userMessage = {
                  text: `[Image: ${selectedImage.name}] ${prompt}`,
                  sender: "user",
                };
                setMessages((prev) => [...prev, userMessage]);

                const formData = new FormData();
                formData.append("image", selectedImage);
                formData.append("text", prompt);

                try {
                  const response = await fetch(
                    "http://localhost:5000/image-chat",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                  }

                  const data = await response.json();
                  const aiMessage = { text: data.response, sender: "ai" };
                  setMessages((prev) => [...prev, aiMessage]);
                } catch (error) {
                  const errorMessage = {
                    text: `Error: ${error.message}`,
                    sender: "error",
                  };
                  setMessages((prev) => [...prev, errorMessage]);
                } finally {
                  setIsLoading(false);
                  setSelectedImage(null);
                  setCurrentInput("");
                }
              }}
              disabled={isLoading || isRecording}
              style={{
                padding: "10px 20px",
                backgroundColor:
                  isLoading || isRecording ? "#6c757d" : "#ffc107",
                color: "black",
                border: "none",
                cursor: isLoading || isRecording ? "not-allowed" : "pointer",
                marginLeft: "10px",
              }}
            >
              Send Image
            </button>
          )}
        </form>
      </div>
    </div>
  );
}

export default App;
