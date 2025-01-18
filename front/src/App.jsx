// eslint-disable-next-line no-unused-vars
import React, { useState, useRef } from "react";
import "./App.css";

const VideoUpload = () => {
  const [recording, setRecording] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResponse, setUploadResponse] = useState(null);
  const [email, setEmail] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioRecorderRef = useRef(null);
  const recordedChunks = useRef([]);
  const audioChunks = useRef([]);
  const isRecordingRef = useRef(false);
  const isFirstRecording = useRef(true);
  const [showPdfMessage, setShowPdfMessage] = useState(false);

  const updateRecordingStatus = async (status) => {
    const formData = new FormData();
    formData.append("email", email);
    formData.append("status", status);

    try {
      await new Promise((resolve) => setTimeout(resolve, 5000));
      await fetch("http://localhost:3000/recording-status", {
        method: "POST",
        body: formData,
      });
    } catch (error) {
      console.error("Error updating recording status:", error);
    }
  };

  const validateEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._-]+@gmail\.com$/;
    return emailRegex.test(email.trim());
  };

  const startRecording = async () => {
    if (!validateEmail(email)) {
      alert("Please enter a valid Gmail address (example@gmail.com)");
      return;
    }
    setShowPdfMessage(false);

    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: { displaySurface: "browser" },
        audio: true,
      });

      screenStream.getVideoTracks()[0].addEventListener("ended", () => {
        stopRecording();
      });

      const videoTrack = screenStream.getVideoTracks()[0];
      const settings = videoTrack.getSettings();

      if (settings.displaySurface !== "browser") {
        screenStream.getTracks().forEach((track) => track.stop());
        alert(
          "W aktualnej wersji aplikacja wspiera tylko wersję przeglądarkowa!"
        );
        throw new Error(
          "W aktualnej wersji aplikacja wspiera tylko wersję przeglądarkowa!"
        );
      }

      const audioStream = new MediaStream([...screenStream.getAudioTracks()]);

      audioRecorderRef.current = new MediaRecorder(audioStream, {
        mimeType: "audio/webm",
      });

      audioRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunks.current.push(event.data);
      };

      audioRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/webm" });
        const audioFile = new File([audioBlob], "recorded_audio.webm", {
          type: "audio/webm",
        });
        await sendAudioToBackend(audioFile);
        audioChunks.current = [];

        if (isRecordingRef.current) {
          audioRecorderRef.current.start();
          setTimeout(() => {
            if (
              audioRecorderRef.current &&
              audioRecorderRef.current.state === "recording"
            ) {
              audioRecorderRef.current.stop();
            }
          }, 30000);
        }
      };

      audioRecorderRef.current.start();
      setTimeout(() => {
        if (
          audioRecorderRef.current &&
          audioRecorderRef.current.state === "recording"
        ) {
          audioRecorderRef.current.stop();
        }
      }, 30000);

      mediaRecorderRef.current = new MediaRecorder(screenStream, {
        mimeType: "video/webm; codecs=vp9",
      });

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) recordedChunks.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(recordedChunks.current, { type: "video/webm" });
        const videoFileForUpload = new File([blob], "recorded_video.webm", {
          type: "video/webm",
        });
        await sendVideoToBackend(videoFileForUpload);
        recordedChunks.current = [];
        if (isRecordingRef.current) {
          setTimeout(() => {
            if (isRecordingRef.current) {
              mediaRecorderRef.current.start();
              setTimeout(() => {
                if (
                  mediaRecorderRef.current &&
                  mediaRecorderRef.current.state === "recording"
                ) {
                  mediaRecorderRef.current.stop();
                }
              }, 2000);
            }
          }, 28000);
        }
      };

      setRecording(true);
      isRecordingRef.current = true;
      await updateRecordingStatus(true);

      if (isFirstRecording.current) {
        setTimeout(() => {
          if (mediaRecorderRef.current) {
            mediaRecorderRef.current.start();
            setTimeout(() => {
              if (
                mediaRecorderRef.current &&
                mediaRecorderRef.current.state === "recording"
              ) {
                mediaRecorderRef.current.stop();
              }
            }, 2000);
          }
        }, 5000);
        isFirstRecording.current = false;
      } else {
        mediaRecorderRef.current.start();
        setTimeout(() => {
          if (
            mediaRecorderRef.current &&
            mediaRecorderRef.current.state === "recording"
          ) {
            mediaRecorderRef.current.stop();
          }
        }, 2000);
      }
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
    if (audioRecorderRef.current) {
      audioRecorderRef.current.stop();
    }
    isRecordingRef.current = false;
    await updateRecordingStatus(false);
    setShowPdfMessage(true);
  };

  const sendVideoToBackend = async (videoFile) => {
    if (!videoFile) {
      alert("Please record a video first!");
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append("video", videoFile);
    formData.append("email", email);

    try {
      const response = await fetch("http://localhost:3000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadResponse({
          success: true,
          message: "Video uploaded successfully!",
          fileName: result.fileName,
          filePath: result.filePath,
        });
      } else {
        setUploadResponse({
          success: false,
          message: result.message || "Failed to upload video.",
        });
      }
    } catch (error) {
      setUploadResponse({
        success: false,
        message: "Error uploading video: " + error.message,
      });
    } finally {
      setUploading(false);
    }
  };

  const sendAudioToBackend = async (audioFile) => {
    if (!audioFile) return;

    const formData = new FormData();
    formData.append("audio", audioFile);
    formData.append("email", email);

    try {
      const response = await fetch("http://localhost:3000/upload-audio", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log("Audio upload result:", result);
    } catch (error) {
      console.error("Error uploading audio:", error);
    }
  };

  return (
    <div className="container">
      <h1>Video Recorder and Upload</h1>
      <div>
        <input
          type="email"
          className="email-input"
          placeholder="Enter your @gmail.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div className="button-container">
        {!recording ? (
          <button onClick={startRecording} className="record-button start">
            Start Recording
          </button>
        ) : (
          <button onClick={stopRecording} className="record-button stop">
            Stop Recording
          </button>
        )}
      </div>

      <div className="upload-status">
        {uploading ? (
          <p>Uploading video...</p>
        ) : (
          <>
            {uploadResponse && (
              <div>
                {uploadResponse.success ? (
                  <div>
                    <p>{uploadResponse.message}</p>
                    <p>Aplikacja działą prawidłowo </p>
                  </div>
                ) : (
                  <p className="error-message">{uploadResponse.message}</p>
                )}
              </div>
            )}
            {showPdfMessage && (
              <p className="pdf-message">
                Jeśli podałeś prawidłowy gmail to w przeciągu nastęonych kilku
                lub kilkunastu minut zostanie wysłany do Ciebie plik pdf
                zawierający informacje o video prezentacji
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default VideoUpload;
