import React, { useState, useRef } from "react";

const VideoUpload = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [recording, setRecording] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResponse, setUploadResponse] = useState(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunks = useRef([]);

  const startRecording = async () => {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });

      const audioStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const combinedStream = new MediaStream([
        ...screenStream.getVideoTracks(),
        ...audioStream.getAudioTracks(),
      ]);

      mediaRecorderRef.current = new MediaRecorder(combinedStream, {
        mimeType: "video/webm; codecs=vp9",
      });
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) recordedChunks.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(recordedChunks.current, {
          type: "video/webm",
        });

        const videoFileForUpload = new File([blob], "recorded_video.webm", {
          type: "video/webm",
        });
        setVideoFile(videoFileForUpload);
        recordedChunks.current = [];
      };
      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (error) {
      console.error("Błąd podczas rozpoczynania nagrywania:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const sendVideoToBackend = async () => {
    if (!videoFile) {
      alert("Please record a video first!");
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append("video", videoFile);

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
    <div>
      <h1>Video Recorder and Upload</h1>
      <div>
        {!recording ? (
          <button
            onClick={startRecording}
            style={{
              backgroundColor: "green",
              color: "white",
              padding: "10px 20px",
              borderRadius: "5px",
            }}
          >
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            style={{
              backgroundColor: "red",
              color: "white",
              padding: "10px 20px",
              borderRadius: "5px",
            }}
          >
            Stop Recording
          </button>
        )}
      </div>

      <div style={{ marginTop: "20px" }}>
        {videoFile && (
          <div>
            <h3>Recorded Video:</h3>
            <video
              src={URL.createObjectURL(videoFile)}
              controls
              style={{ width: "100%", maxWidth: "600px" }}
            />
          </div>
        )}
      </div>

      <div style={{ marginTop: "20px" }}>
        <button
          onClick={sendVideoToBackend}
          disabled={uploading || !videoFile}
          style={{
            backgroundColor: uploading ? "gray" : "blue",
            color: "white",
            padding: "10px 20px",
            borderRadius: "5px",
          }}
        >
          {uploading ? "Uploading..." : "Upload Video"}
        </button>
      </div>

      {uploadResponse && (
        <div style={{ marginTop: "20px" }}>
          {uploadResponse.success ? (
            <div>
              <p>{uploadResponse.message}</p>
              <p>File Name: {uploadResponse.fileName}</p>
              <p>File Path: {uploadResponse.filePath}</p>
            </div>
          ) : (
            <p style={{ color: "red" }}>{uploadResponse.message}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoUpload;
