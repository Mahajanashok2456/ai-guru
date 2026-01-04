import { useState, useEffect, useRef } from 'react';
import { transcribeAudio, sendVoiceMessage } from '../services/api';

export const useVoice = (setCurrentInput, onSubmit, currentSessionId, activeRequestsRef) => {
  const [recognition, setRecognition] = useState(null);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechInterimResult, setSpeechInterimResult] = useState("");
  const [speechError, setSpeechError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isConverting, setIsConverting] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = "en-US";

      recognitionInstance.onstart = () => {
        setIsListening(true);
        setSpeechError(null);
      };

      recognitionInstance.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        if (event.error === "not-allowed") {
          setSpeechError("Microphone access denied. Please enable it in browser settings.");
        } else if (event.error === "no-speech") {
          // Ignore no-speech errors to stay listening
        } else {
          setSpeechError(`Voice error: ${event.error}`);
        }
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      recognitionInstance.onresult = (event) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        if (finalTranscript) {
          setCurrentInput((prev) => (prev ? `${prev} ${finalTranscript}` : finalTranscript));
        }
        setSpeechInterimResult(interimTranscript);
      };

      setRecognition(recognitionInstance);
      setSpeechSupported(true);
    } else {
      console.warn("Speech recognition not supported in this browser.");
    }
  }, [setCurrentInput]);

  const startSpeechRecognition = () => {
    if (recognition && !isListening) {
      try {
        setSpeechInterimResult("");
        recognition.start();
      } catch (e) {
        console.error("Recognition start error:", e);
      }
    }
  };

  const stopSpeechRecognition = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  const handleVoiceInput = () => {
    if (isListening) {
      stopSpeechRecognition();
    } else {
      startSpeechRecognition();
    }
  };

  const clearTranscription = () => {
    setCurrentInput("");
    setSpeechInterimResult("");
  };

  const processVoiceMessage = async (audioBlob, sender = "user") => {
    try {
      setIsConverting(true);
      const controller = new AbortController();
      activeRequestsRef.current.set("voice", controller);

      const data = await sendVoiceMessage(audioBlob, currentSessionId, controller.signal);
      
      // The actual handling of the response (updating messages) will happen in App.js
      // or we can pass a callback here. To keep logic simple, we'll return the data.
      return data;
    } catch (error) {
      if (error.name !== "AbortError") {
        console.error("Error processing voice message:", error);
        throw error;
      }
    } finally {
      setIsConverting(false);
      activeRequestsRef.current.delete("voice");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleVoiceRecording = async () => {
    if (isRecording) {
      stopRecording();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        // Use a callback to handle the result in App.js
        if (onSubmit && typeof onSubmit === 'function') {
           // We can't directly submit here because App.js handles the message state
           // but we can pass the blob back or handle it here if it returns data
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Microphone access error:", error);
      setSpeechError("Could not access microphone.");
    }
  };

  return {
    speechSupported,
    isListening,
    speechInterimResult,
    speechError,
    isRecording,
    isConverting,
    handleVoiceInput,
    handleVoiceRecording,
    clearTranscription,
    processVoiceMessage,
    setSpeechError
  };
};
