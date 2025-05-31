import React from "react";
import catImg from "./cat.png";
import "./MicButton.css";

const MicButton = ({ onClick, isRecording }) => {
  return (
    <button className={`cat-button ${isRecording ? "listening" : ""}`} onClick={onClick}>
      <img src={catImg} alt="Cat mic button" className="cat-image" />
    </button>
  );
};

export default MicButton;
