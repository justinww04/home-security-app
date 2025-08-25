import React, { useEffect, useState } from "react";
import { api, wsURL } from "../api";


type EventItem = {
  id: number;
  timestamp: string;
  label: string;
  confidence?: number;
  camera: string;
  snapshot_path?: string;
  person?: string;
};

export default function EventFeed() {
  const [items, setItems] = useState<EventItem[]>([]);

  useEffect(() => {
  api.getEvents().then((data) => setItems(data));

    // Optional: live updates via WebSocket (if backend supports it)
    const ws = new WebSocket("ws://localhost:8000/ws/events");
    ws.onmessage = (ev) => {
      const obj = JSON.parse(ev.data);
      setItems(prev => [{ ...obj }, ...prev].slice(0, 50));
    };
    const ping = setInterval(() => {
      if (ws.readyState === 1) ws.send("ping");
    }, 15000);

    return () => {
      clearInterval(ping);
      ws.close();
    };
  }, []);

  return (
    <div className="card">
      <h2>Events</h2>
      <div>
        {items.map(e => (
          <div key={e.id} className="feed-item">
            <div>
              <span className="badge">{e.camera}</span>{" "}
              <strong>{e.label}</strong>{" "}
              {e.confidence ? `(${e.confidence.toFixed(2)})` : ""}
            </div>
            <div className="small">
              {new Date(e.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}