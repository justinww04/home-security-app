import React, { useState } from "react";
import { api } from "../api";

const ANGLES = ["left", "right", "up", "down", "center"] as const;
type Angle = typeof ANGLES[number];

export default function EnrollWizard() {
  const [name, setName] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [angleIndex, setAngleIndex] = useState(0);
  const [countForAngle, setCountForAngle] = useState(0);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  const needAngle = ANGLES[angleIndex];

  async function start() {
    if (!name.trim()) return;
    const session = await api.startEnrollment(name);
    setSessionId(session.session_id);
    setAngleIndex(0);
    setCountForAngle(0);
    setDone(false);
  }

  async function captureOnce() {
    if (!sessionId) return;
    setBusy(true);
    try {
      const snap = await api.getSnapshot();
      const b64 = await blobToDataURL(snap);
      await api.captureEnrollment(sessionId, needAngle, b64);
      const nextCount = countForAngle + 1;
      setCountForAngle(nextCount);
      if (nextCount >= 4) {
        if (angleIndex + 1 < ANGLES.length) {
          setAngleIndex(angleIndex + 1);
          setCountForAngle(0);
        } else {
          await api.finishEnrollment(sessionId);
          setDone(true);
          setSessionId(null);
        }
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <h2>Enroll Face</h2>
      {!sessionId && !done && (
        <>
          <label>Name</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Type a name, e.g. Justin"
          />
          <div style={{ marginTop: 8 }}>
            <button onClick={start} disabled={!name.trim()}>
              Start Scan
            </button>
          </div>
        </>
      )}

      {sessionId && (
        <>
          <div style={{ margin: "8px 0" }}>
            Angle: <strong>{needAngle.toUpperCase()}</strong> &nbsp; Progress: {countForAngle}/4
          </div>
          <div className="small">Tip: Hold the requested angle steady. Press “Capture” 4 times per angle.</div>
          <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
            <button onClick={captureOnce} disabled={busy}>
              Capture
            </button>
          </div>
        </>
      )}

      {done && (
        <div style={{ marginTop: 8 }}>
          <div className="badge">Complete</div>
          <div>Your face should now be recognized.</div>
        </div>
      )}
    </div>
  );
}

function blobToDataURL(blob: Blob): Promise<string> {
  return new Promise((res) => {
    const reader = new FileReader();
    reader.onloadend = () => res(reader.result as string);
    reader.readAsDataURL(blob);
  });
}