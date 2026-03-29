import React, { useEffect, useState, useCallback } from "react";
import "./App.css";

// ⚠️ Change this later to your deployed backend (Render)
const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [floorData, setFloorData] = useState({});
  const [selectedFloor, setSelectedFloor] = useState("1");
  const [config, setConfig] = useState({ mode: "image", source: "", floor_id: 1 });
  const [analytics, setAnalytics] = useState(null);

  // ✅ FIXED: Login state
  const [isLoggedIn] = useState(true);

  // ✅ FIXED: Reserve function
  const handleReserve = (seatId) => {
    console.log("Reserving seat:", seatId);

    fetch(`${API_BASE}/reserve`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ seat_id: seatId, floor_id: selectedFloor }),
    })
      .then((res) => res.json())
      .then(() => fetchGlobalData())
      .catch(console.error);
  };

  const FLOOR_INFO = {
    "1": { subject: "Periodicals & Children Section", sockets: 24, totalSockets: 30 },
    "2": { subject: "Tamil Books Section", sockets: 12, totalSockets: 40 },
    "3": { subject: "Comp Sci, Philosophy & Religion", sockets: 45, totalSockets: 60 },
    "4": { subject: "Economics, Law & Literature", sockets: 18, totalSockets: 25 },
    "5": { subject: "Math, Gen Science & Medicine", sockets: 32, totalSockets: 50 },
    "6": { subject: "Engineering & Management", sockets: 55, totalSockets: 80 },
    "7": { subject: "History & Digital Library", sockets: 10, totalSockets: 100 },
    "8": { subject: "Administrative Sections", sockets: 2, totalSockets: 10 },
  };

  const processFloorData = (data) => {
    const rawData = { ...data };
    Object.keys(FLOOR_INFO).forEach((fid) => {
      if (!rawData[fid]) {
        rawData[fid] = {
          available: 10,
          occupied: 5,
          reserved: 2,
          last_updated: new Date().toISOString(),
          seats: {},
          boxes: [],
        };
      }
    });
    setFloorData(rawData);
  };

  const fetchGlobalData = useCallback(() => {
    fetch(`${API_BASE}/floors`)
      .then((res) => res.json())
      .then(processFloorData)
      .catch(console.error);

    fetch(`${API_BASE}/analytics`)
      .then((res) => res.json())
      .then(setAnalytics)
      .catch(console.error);

    fetch(`${API_BASE}/config`)
      .then((res) => res.json())
      .then(setConfig)
      .catch(console.error);
  }, []);

  useEffect(() => {
    fetchGlobalData();
    const interval = setInterval(fetchGlobalData, 3000);
    return () => clearInterval(interval);
  }, [fetchGlobalData]);

  const updateConfig = (updates) => {
    fetch(`${API_BASE}/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    })
      .then((res) => res.json())
      .then((data) => setConfig(data.config))
      .catch(console.error);
  };

  const currentData =
    floorData[selectedFloor] || { available: 0, occupied: 0, reserved: 0, seats: {}, boxes: [] };

  const seatColor = (status) => {
    if (status === "OCCUPIED") return "rgba(239, 68, 68, 0.7)";
    if (status === "RESERVED") return "rgba(250, 204, 21, 0.7)";
    return "rgba(34, 197, 94, 0.5)";
  };

  return (
    <div className="app">
      <header>
        <h1>🏢 Seatify Library Dashboard</h1>
        <div>Live • {new Date().toLocaleTimeString()}</div>
      </header>

      <div className="main-layout">
        <aside>
          {Object.keys(floorData).map((fid) => (
            <div key={fid} onClick={() => setSelectedFloor(fid)}>
              Floor {fid}
            </div>
          ))}
        </aside>

        <main>
          <h2>Floor {selectedFloor}</h2>

          <div>
            Available: {currentData.available} | Occupied: {currentData.occupied}
          </div>

          {/* Seat Boxes */}
          {(currentData.boxes || []).map((box, i) => (
            <div key={i}>
              Seat {box.id} - {box.status}

              {isLoggedIn && box.status === "EMPTY" && (
                <button onClick={() => handleReserve(box.id)}>Reserve</button>
              )}
            </div>
          ))}
        </main>
      </div>
    </div>
  );
}

export default App;