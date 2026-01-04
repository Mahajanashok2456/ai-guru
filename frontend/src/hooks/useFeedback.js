import { useState } from 'react';
import { submitFeedbackToAPI } from '../services/api';

export const useFeedback = (setMessages) => {
  const [feedbackLoading, setFeedbackLoading] = useState(new Set());

  const submitFeedback = async (interactionId, sessionId, feedbackType) => {
    try {
      setFeedbackLoading((prev) => new Set([...prev, interactionId]));

      const data = await submitFeedbackToAPI(interactionId, sessionId, feedbackType);

      // Update the local messages to show feedback confirmation
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.interactionId === interactionId
            ? {
                ...msg,
                feedbackSubmitted: feedbackType,
                feedbackMessage: data.feedback_message || "Thank you for your feedback!",
              }
            : msg
        )
      );
    } catch (error) {
      console.error("Error submitting feedback:", error);
    } finally {
      setFeedbackLoading((prev) => {
        const newSet = new Set(prev);
        newSet.delete(interactionId);
        return newSet;
      });
    }
  };

  return {
    feedbackLoading,
    submitFeedback
  };
};
