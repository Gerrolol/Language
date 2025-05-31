import { useState } from "react";
import MicButton from "./components/MicButton";

const App = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [outputText, setOutputText] = useState("Press start to record...");
  const [translationData, setTranslationData] = useState(null);
  const [showEnglish, setShowEnglish] = useState(false);
  const [error, setError] = useState(null);

  // Configure API URL based on environment
  const API_BASE_URL = import.meta.env.PROD
    ? 'https://translatethai.onrender.com'  // Replace with your deployed backend URL
    : 'http://localhost:5000';

  const handleTranscription = async (audioBlob) => {
  setError(null);
  setIsProcessing(true);
  setOutputText("Processing...");

  try {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");  // Changed filename

    const response = await fetch(`${API_BASE_URL}/transcribe`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    
    if (!response.ok || data.error) {
      throw new Error(data.error || "Unknown server error");
    }

    if (!data.english || !data.thai) {
      throw new Error("Invalid response from server");
    }

    setTranslationData(data);
    setOutputText(data.thai);
    setShowEnglish(false);
    
  } catch (err) {
    console.error("Transcription error:", err);
    setError(err.message || "Processing failed. Please try again.");
    setOutputText("Error processing audio");
    
    // For debugging - remove in production
    if (err.message.includes("Failed to fetch")) {
      setError("Could not connect to server. Is the backend running?");
    }
  } finally {
    setIsProcessing(false);
  }
};

  const toggleLanguage = () => {
    if (translationData) {
      setOutputText(showEnglish ? translationData.thai : translationData.english);
      setShowEnglish(!showEnglish);
    }
  };

  return (
    <div className="app-container">
      <div className="cat-section">
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="speech-bubble-container">
          {outputText && (
            <div className="speech-bubble">
              {outputText}
            </div>
          )}
          {translationData && !isProcessing && (
            <button 
              onClick={toggleLanguage}
              className="language-toggle"
            >
              {showEnglish ? "แสดงภาษาไทย" : "Show English"}
            </button>
          )}
        </div>

        <MicButton onTranscribe={handleTranscription} />
      </div>
      <h1 className="title">Jennie's translator from Gello 💕</h1>
    </div>
  );
};

export default App;

