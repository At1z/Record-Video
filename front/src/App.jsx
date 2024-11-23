import React, { useState, useRef } from "react";

const VideoUpload = () => {
  const [recording, setRecording] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResponse, setUploadResponse] = useState(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunks = useRef([]);
  const intervalRef = useRef(null);
  const isRecordingRef = useRef(false);

  const startRecording = async () => {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });

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
      }, 20000);
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

    try {
      const response = await fetch("http://127.0.0.1:8000/api/upload/", {
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
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        textAlign: "center",
        padding: "20px",
      }}
    >
      <h1>Video Recorder and Upload</h1>

      <div style={{ marginTop: "20px" }}>
        {!recording ? (
          <button
            onClick={startRecording}
            style={{
              backgroundColor: "green",
              color: "white",
              padding: "10px 20px",
              borderRadius: "5px",
              marginBottom: "20px",
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
              marginBottom: "20px",
            }}
          >
            Stop Recording
          </button>
        )}
      </div>

      <div style={{ marginTop: "20px" }}>
        {uploadResponse && (
          <div>
            {uploadResponse.success ? (
              <div>
                <p>{uploadResponse.message}</p>
                <p>File is uploaded to /videos in video_upload/videos </p>
              </div>
            ) : (
              <p style={{ color: "red" }}>{uploadResponse.message}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoUpload;
