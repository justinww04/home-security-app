import React from "react";
import { videoURL } from "../api";

const VIDEO_URL = import.meta.env.VITE_VIDEO_URL ?? "http://localhost:8000/video";

export default function LiveView() {
  return (
    <div className="card">
      <h2>Live View</h2>
      <img src={videoURL} alt="live" />
    </div>
  );
}