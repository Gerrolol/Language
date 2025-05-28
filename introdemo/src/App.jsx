import { useState } from "react"; 
import MicButton from "./components/MicButton";

const App = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [outputText, setOutputText] = useState("");

  const handleMicClick = () => {
    setIsRecording(!isRecording); 
    // For testing: simulate translation output
    if (!isRecording) {
      setOutputText("This is where translated text will show");
    } else {
      setOutputText("");
    }

  };

  return (
    <div>
      <h1>Mic Recorder</h1>
      <MicButton onClick={handleMicClick} text={isRecording ? "Stop" : "Start"} />
      <textarea 
        readOnly 
        value={outputText} 
        rows={5} 
        cols={50} 
        placeholder="Translated text will appear here..."
      />
    </div>
  );
};

export default App; 





