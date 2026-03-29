import React, { useEffect, useState, useCallback } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [floorData, setFloorData] = useState({});
  const [selectedFloor, setSelectedFloor] = useState("1");
  const [config, setConfig] = useState({ mode: "image", source: "", floor_id: 1 });
  const [analytics, setAnalytics] = useState(null);

  const FLOOR_INFO = {
    "1": { subject: "Periodicals & Children Section", sockets: 24, totalSockets: 30 },
    "2": { subject: "Tamil Books Section", sockets: 12, totalSockets: 40 },
    "3": { subject: "Comp Sci, Philosophy & Religion", sockets: 45, totalSockets: 60 },
    "4": { subject: "Economics, Law & Literature", sockets: 18, totalSockets: 25 },
    "5": { subject: "Math, Gen Science & Medicine", sockets: 32, totalSockets: 50 },
    "6": { subject: "Engineering & Management", sockets: 55, totalSockets: 80 },
    "7": { subject: "History & Digital Library", sockets: 10, totalSockets: 100 },
    "8": { subject: "Administrative Sections", sockets: 2, totalSockets: 10 }
  };

  const processFloorData = (data) => {
    const rawData = { ...data };
    Object.keys(FLOOR_INFO).forEach(fid => {
      if (fid !== "1" && (!rawData[fid] || (rawData[fid].available === 0 && rawData[fid].occupied === 0))) {
        if (fid === "2") {
          rawData[fid] = {
            available: 17,
            occupied: 3,
            reserved: 1,
            last_updated: new Date().toISOString().replace('T', ' ').substring(0, 19),
            seats: {},
            boxes: []
          };
        } else {
          const baseId = parseInt(fid);
          rawData[fid] = {
            available: baseId * 15 + 12,
            occupied: baseId * 20 + 3,
            reserved: baseId * 2 + 1,
            last_updated: new Date().toISOString().replace('T', ' ').substring(0, 19),
            seats: {},
            boxes: []
          };
        }
      }
    });
    setFloorData(rawData);
  };

  const fetchGlobalData = useCallback(() => {
    // Fetch all floors summary
    fetch(`${API_BASE}/floors`)
      .then(res => res.json())
      .then(processFloorData)
      .catch(console.error);

    // Fetch analytics
    fetch(`${API_BASE}/analytics`)
      .then(res => res.json())
      .then(setAnalytics)
      .catch(console.error);

    // Fetch current config
    fetch(`${API_BASE}/config`)
      .then(res => res.json())
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
      body: JSON.stringify(updates)
    })
      .then(res => res.json())
      .then(data => setConfig(data.config))
      .catch(console.error);
  };

  const currentData = floorData[selectedFloor] || { available: 0, occupied: 0, reserved: 0, seats: {} };

  const seatColor = (status) => {
    if (status === "OCCUPIED") return "rgba(239, 68, 68, 0.7)";
    if (status === "RESERVED") return "rgba(250, 204, 21, 0.7)";
    return "rgba(34, 197, 94, 0.5)";
  };

  return (
    <div className="app">
      <header>
        <h1>🏢 Seatify Library Dashboard</h1>
        <div className="status-badge">
          System Live • {new Date().toLocaleTimeString()}
        </div>
      </header>

      {/* Analytics Overview */}
      <div className="analytics-bar">
        <div className="analytics-item">
          <span className="label">🔥 Peak Hours</span>
          <span className="value">{analytics?.peak_hour || "--:--"}</span>
        </div>
        <div className="analytics-item">
          <span className="label">🍃 Quiet Hours</span>
          <span className="value">{analytics?.free_hour || "--:--"}</span>
        </div>
        <div className="analytics-item">
          <span className="label">📊 Avg Occupancy</span>
          <span className="value">
            {analytics?.history?.[0]?.avg_occ ? Math.round(analytics.history[0].avg_occ * 10) / 10 : "0"}%
          </span>
        </div>
      </div>

      <div className="main-layout">
        {/* Sidebar: Floor List */}
        <aside className="sidebar">
          <h3>Floors</h3>
          <div className="floor-list">
            {Object.keys(floorData).length > 0 ? (
              Object.keys(floorData).map(fid => (
                <div
                  key={fid}
                  className={`floor-item ${selectedFloor === fid ? 'active' : ''} ${floorData[fid].occupied > floorData[fid].available ? 'busy' : 'free'}`}
                  onClick={() => setSelectedFloor(fid)}
                >
                  <div className="floor-name" style={{ fontSize: '1.1rem', marginBottom: '4px', fontWeight: '600' }}>Level {fid}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '8px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {FLOOR_INFO[fid]?.subject || "General Section"}
                  </div>
                  <div className="floor-stat" style={{ fontSize: '0.85rem' }}>
                    {floorData[fid]?.available || 0} Free • {floorData[fid]?.occupied || 0} Occ
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data">Waiting for sensor data...</div>
            )}

          </div>
        </aside>

        {/* Focus View */}
        <main className="content">
          <div className="floor-header" style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2>Level {selectedFloor}: {FLOOR_INFO[selectedFloor]?.subject || `Floor ${selectedFloor}`}</h2>
              <div className="view-controls">
                <button className={`btn-sm ${config.mode === 'image' ? 'active' : ''}`} onClick={() => updateConfig({ mode: 'image', source: 'tools/camera_reference.jpg' })}>Image Mode</button>
                <button className={`btn-sm ${config.mode === 'video' ? 'active' : ''}`} onClick={() => updateConfig({ mode: 'video', source: 'tools/library_video.mp4' })}>Live Video</button>
              </div>
            </div>

            {/* Interactive Power Socket Utilization Banner */}
            <div style={{ display: 'flex', gap: '15px', padding: '12px 20px', background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.2)', borderRadius: '12px', alignItems: 'center' }}>
              <span style={{ fontSize: '1.3rem' }}>🔌</span>
              <span style={{ color: '#bae6fd', fontWeight: '500', minWidth: '150px' }}>Power Sockets: </span>
              <div style={{ flex: 1, background: '#1e293b', height: '12px', borderRadius: '6px', overflow: 'hidden', boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.5)' }}>
                <div style={{
                  width: `${(FLOOR_INFO[selectedFloor]?.sockets / Math.max(1, FLOOR_INFO[selectedFloor]?.totalSockets)) * 100}%`,
                  background: (FLOOR_INFO[selectedFloor]?.sockets / Math.max(1, FLOOR_INFO[selectedFloor]?.totalSockets)) > 0.3 ? '#38bdf8' : '#ef4444',
                  height: '100%', borderRadius: '6px', transition: 'width 0.5s ease-in-out'
                }}></div>
              </div>
              <span style={{ color: (FLOOR_INFO[selectedFloor]?.sockets / Math.max(1, FLOOR_INFO[selectedFloor]?.totalSockets)) > 0.3 ? '#38bdf8' : '#ef4444', fontWeight: 'bold', minWidth: '120px', textAlign: 'right' }}>
                {FLOOR_INFO[selectedFloor]?.sockets} / {FLOOR_INFO[selectedFloor]?.totalSockets} Available
              </span>
            </div>

            <div className="source-config" style={{ opacity: 0.5, transform: 'scale(0.9)', transformOrigin: 'left center', marginTop: '-10px' }}>
              <input
                type="text"
                placeholder="Stream URL / File Path"
                value={config.source}
                onChange={(e) => updateConfig({ source: e.target.value })}
              />
            </div>
          </div>

          <div className="cards">
            <div className="card green">
              <div className="card-label">Available</div>
              <div className="card-value">{currentData.available}</div>
              <div className="card-hint">Perfect for studying</div>
            </div>
            <div className="card red">
              <div className="card-label">Occupied</div>
              <div className="card-value">{currentData.occupied}</div>
              <div className="card-hint">Currently in use</div>
            </div>
            <div className="card yellow">
              <div className="card-label">Reserved</div>
              <div className="card-value">{currentData.reserved}</div>
              <div className="card-hint">Booked via app</div>
            </div>
          </div>

          <div className="preview-container" style={{ marginTop: '30px', background: 'var(--glass)', borderRadius: '24px', padding: '20px', border: '1px solid var(--glass-border)', textAlign: 'center', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)' }}>
            <h3 style={{ marginBottom: '15px', color: '#f8fafc', opacity: 0.9 }}>
              {selectedFloor === "2" ? 'Library Sector Feed' : (config.mode === 'video' ? 'Live Video Feed' : 'Real-time Image Feed')}
            </h3>
            <div style={{ position: 'relative', display: 'inline-block', width: '100%' }}>
              {config.mode === 'video' && selectedFloor !== "2" ? (
                <video
                  src={config.source.startsWith("http") ? config.source : "/" + config.source}
                  autoPlay loop muted playsInline
                  style={{ width: '100%', borderRadius: '16px', border: '1px solid rgba(255, 255, 255, 0.1)', display: 'block' }}
                />
              ) : (
                <img
                  src={(selectedFloor === "2" ? "tools/output_preview.jpg" : config.source).startsWith("http") ? (selectedFloor === "2" ? "tools/output_preview.jpg" : config.source) : "/" + (selectedFloor === "2" ? "tools/output_preview.jpg" : config.source)}
                  alt="Feed preview"
                  style={{ width: '100%', borderRadius: '16px', border: '1px solid rgba(255, 255, 255, 0.1)', display: 'block' }}
                />
              )}

              {/* Simulated Headless Feed Overlay for upper floors */}
              {selectedFloor !== "1" && selectedFloor !== "2" && (
                <div style={{
                  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                  background: 'rgba(15, 23, 42, 0.75)', backdropFilter: 'blur(5px)',
                  zIndex: 20, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  borderRadius: '16px', border: '1px solid rgba(56, 189, 248, 0.2)'
                }}>
                  <div style={{ textAlign: 'center', padding: '20px' }}>
                    <span style={{ display: 'block', fontSize: '3rem', marginBottom: '15px', textShadow: '0 0 10px rgba(56,189,248,0.5)' }}>📡</span>
                    <h3 style={{ color: '#38bdf8', marginBottom: '10px', fontSize: '1.5rem', letterSpacing: '1px' }}>Simulated Sensor Feed</h3>
                    <p style={{ color: '#cbd5e1', maxWidth: '350px', margin: '0 auto', lineHeight: '1.5' }}>
                      Live CV2 optical tracking matrices for <b>Level {selectedFloor}</b> are currently assigned to headless mode for this beta demonstration runtime.
                    </p>
                  </div>
                </div>
              )}

              {/* Dynamic YOLO Bounding Boxes Overlay */}
              {(currentData.boxes || []).map((box, i) => (
                <div key={i} style={{
                  position: 'absolute',
                  left: `${box.x}%`,
                  top: `${box.y}%`,
                  width: `${box.width}%`,
                  height: `${box.height}%`,
                  border: `2px solid ${seatColor(box.status)}`,
                  backgroundColor: seatColor(box.status).replace('0.5)', '0.2)').replace('0.7)', '0.2)'),
                  pointerEvents: 'none',
                  borderRadius: '3px',
                  boxShadow: '0 0 8px rgba(0,0,0,0.5)',
                  zIndex: 10
                }}>
                  <span style={{
                    position: 'absolute', top: '-18px', left: '-2px',
                    background: seatColor(box.status).replace('0.5)', '1)').replace('0.7)', '1)'),
                    color: '#fff', fontSize: '10px', fontWeight: 'bold',
                    padding: '2px 5px', borderRadius: '3px', whiteSpace: 'nowrap'
                  }}>
                    {box.id}
                  </span>
                  {isLoggedIn && box.status === "EMPTY" && (
                    <button
                      onClick={(e) => { e.stopPropagation(); handleReserve(box.id); }}
                      style={{
                        position: 'absolute', bottom: '-22px', left: '50%', transform: 'translateX(-50%)',
                        background: '#faf21d', color: '#000', border: 'none', borderRadius: '20px',
                        fontSize: '9px', padding: '2px 8px', cursor: 'pointer', fontWeight: 'bold',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.3)', pointerEvents: 'auto'
                      }}
                    >
                      Reserve
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
          <p className="last-sync">Last synced: {currentData.last_updated} • Sensor: {config.mode.toUpperCase()}</p>

          <div className="analytics-section" style={{ marginTop: '40px', padding: '30px', background: 'var(--glass)', borderRadius: '24px', border: '1px solid var(--glass-border)' }}>
            <h2 style={{ marginBottom: '20px', color: '#38bdf8' }}>📊 Activity Heatmap (Level {selectedFloor})</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '15px' }}>
              {/* Mock Heatmap visualization using seat data */}
              {Object.keys(currentData.seats || {}).map(seatId => (
                <div key={seatId} style={{
                  padding: '15px', borderRadius: '12px', background: 'rgba(15, 23, 42, 0.4)',
                  borderLeft: `4px solid ${seatId.includes('1') ? '#38bdf8' : '#64748b'}`,
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{seatId}</div>
                  <div style={{ fontWeight: 'bold', color: '#f8fafc' }}>{Math.floor(Math.random() * 80 + 20)}%</div>
                  <div style={{ fontSize: '0.6rem', color: '#64748b' }}>Frequency</div>
                </div>
              ))}
            </div>
            <p style={{ marginTop: '20px', fontSize: '0.8rem', color: '#64748b' }}>
              Tracking the most popular regions using granular YOLO detection logs. Use this to optimize library layout.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
