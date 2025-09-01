
import React, { useEffect, useState } from "react";
import LiveView from "./components/LiveView";
import EnrollWizard from "./components/EnrollWizard";
import EventFeed from "./components/EventFeed";
import { api } from "./api";
import ActiveTab from "./components/ActiveTab";

export default function App() {
  const [health, setHealth] = useState<"up" | "down">("down");

  useEffect(() => {
    api.getHealth()
      .then(() => setHealth("up"))
      .catch(() => setHealth("down"));
  }, []);
  return (
    <>
      <header>
        <div
          className="container"
          style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
        >
          <h1>Home Security</h1>
          <div className="badge">
            {health === "up" ? "Backend: Online" : "Backend: Offline"}
          </div>
        </div>
      </header>

      <div className="container">
        <div className="grid">
          <div>
            <LiveView />
            <div style={{ height: 12 }} />
            <EventFeed />
          </div>

         <div>
  <EnrollWizard />
  <ActiveTab />

  <div className="card" style={{ marginTop: 12 }}>
    <h2>How it works</h2>
    <ul>
      <li>
        Click <em>Start Scan</em>, enter a name, then capture 4 images for each prompted angle.
      </li>
      <li>Stand in front of the camera afterwards; detections will appear in Events.</li>
      <li>Phase 1 prints detections to the server console. We’ll add push/SMS next.</li>
    </ul>
  </div>
</div>
        </div>
      </div>
    </>
  );
}
