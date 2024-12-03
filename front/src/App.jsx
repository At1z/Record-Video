import React, { useState, useRef } from "react";
import "./App.css";

const VideoUpload = () => {
  const [recording, setRecording] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResponse, setUploadResponse] = useState(null);
  const [email, setEmail] = useState("");
  const mediaRecorderRef = useRef(null);
  const recordedChunks = useRef([]);
  const intervalRef = useRef(null);
  const isRecordingRef = useRef(false);

  const startRecording = async () => {
    if (!email || !email.includes("@gmail.com")) {
      alert("Please enter a valid email address before starting the recording");
      return;
    }

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

      const combinedStream = new MediaStream([
        ...screenStream.getVideoTracks(),
        ...screenStream.getAudioTracks(),
      ]);

      mediaRecorderRef.current = new MediaRecorder(combinedStream, {
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
          mediaRecorderRef.current.start();
        }
      };
      mediaRecorderRef.current.start();
      setRecording(true);
      isRecordingRef.current = true;
      intervalRef.current = setInterval(() => {
        if (
          mediaRecorderRef.current &&
          mediaRecorderRef.current.state === "recording"
        ) {
          mediaRecorderRef.current.stop();
        }
      }, 30000);
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };
  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      clearInterval(intervalRef.current);
      isRecordingRef.current = false;
      setRecording(false);
    }
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
          uploadResponse && (
            <div>
              {uploadResponse.success ? (
                <div>
                  <p>{uploadResponse.message}</p>
                  <p>File is uploaded to /videos in video_upload/videos </p>
                </div>
              ) : (
                <p className="error-message">{uploadResponse.message}</p>
              )}
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default VideoUpload;
