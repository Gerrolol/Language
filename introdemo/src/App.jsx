import { useState } from "react";
import MicButton from "./components/MicButton";

const App = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [outputText, setOutputText] = useState("Press start to record...");
  const [translationData, setTranslationData] = useState(null);
  const [showEnglish, setShowEnglish] = useState(false);
  const [error, setError] = useState(null);

  // Configure API URL based on environment
  const API_BASE_URL = import.meta.env.PROD 
    ? 'https://your-backend-url.com'  // Replace with your deployed backend URL
    : 'http://localhost:5000';

  const handleMicClick = async () => {
    setError(null); // Reset error state
    
    if (!isRecording && !isProcessing) {
      // Start recording
      setIsRecording(true);
      setOutputText("Recording...");
      try {
        const response = await fetch(`${API_BASE_URL}/start`);
        if (!response.ok) {
          throw new Error('Failed to start recording');
        }
      } catch (err) {
        console.error(err);
        setError(err.message);
        setOutputText("Error starting recording");
        setIsRecording(false);
      }
    } else if (isRecording) {
      // Stop recording and process
      setIsRecording(false);
      setIsProcessing(true);
      setOutputText("Processing...");
      
      try {
        const response = await fetch(`${API_BASE_URL}/stop`);
        if (!response.ok) {
          throw new Error('Failed to process recording');
        }
        
        const data = await response.json();
        
        // Handle backend errors
        if (data.error) {
          throw new Error(data.error);
        }
        
        setTranslationData(data);
        setOutputText(data.thai); // Show Thai first as requested
        setShowEnglish(false); // Keep Thai as default view
      } catch (err) {
        console.error(err);
        setError(err.message);
        setOutputText(err.message || "Error processing recording");
      } finally {
        setIsProcessing(false);
      }
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
        {/* Error message display */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {/* Speech bubble and toggle */}
        <div className="speech-bubble-container">
          {outputText && (
            <div className="speech-bubble">
              {outputText}
            </div>
          )}
          {translationData && !isRecording && !isProcessing && (
            <button 
              onClick={toggleLanguage}
              className="language-toggle"
            >
              {showEnglish ? "แสดงภาษาไทย" : "Show English"}
            </button>
          )}
        </div>
        
        {/* Mic Button */}
        <MicButton onClick={handleMicClick} isRecording={isRecording} />
      </div>
      <h1 className="title">Jennie's translator from Gello 💕</h1>
    </div>
  );
};

export default App;