import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";
import Navbar from "./Navbar";

export default function MLMonitor({ apiBase = "/api" }) {
  const { token, user } = useContext(AuthContext);
  const [statuses, setStatuses] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchStatuses = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${apiBase}/servers/ml/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatuses(res.data);
    } catch (e) {
      console.error("Failed to load ML Statuses", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatuses();
    const interval = setInterval(fetchStatuses, 5000);
    return () => clearInterval(interval);
  }, [token, apiBase]);

  const handleReset = async (source) => {
    if (!window.confirm(`Are you sure you want to RESET the ML Brain for ${source}? It will forget all patterns.`)) return;
    try {
      await axios.post(`${apiBase}/servers/ml/reset`, { source }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchStatuses();
    } catch (e) {
      alert("Failed to reset: " + e.message);
    }
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="app-wrapper">
      <Navbar />
      <div className="container animate-fade-in" style={{ maxWidth: 1000, margin: '0 auto', paddingTop: 40 }}>
        
        <div style={{ marginBottom: 40, display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
            <div>
                <h1 style={{ margin: 0, fontSize: 28, textTransform: 'uppercase', letterSpacing: 2 }}>Machine Learning Control</h1>
                <p style={{ margin: "10px 0 0 0", color: "var(--muted)" }}>Monitor and manage isolated Anomaly Detection models per server.</p>
            </div>
            <div className="badge ok" style={{ fontSize: 12, padding: "6px 12px" }}>ENGINE ONLINE</div>
        </div>

        {loading ? (
            <div style={{ textAlign: "center", color: "var(--muted)", padding: 40 }}>Loading Models...</div>
        ) : statuses.length === 0 ? (
            <div className="card" style={{ textAlign: "center", padding: 40 }}>
                <div style={{ fontSize: 40, marginBottom: 10 }}>🧠</div>
                <h3 style={{ margin: 0 }}>No ML Models Found</h3>
                <p style={{ color: "var(--muted)", margin: "10px 0 0 0" }}>Start your agents to begin collecting telemetry.</p>
            </div>
        ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 24 }}>
                {statuses.map(s => {
                    const isTraining = s.mode === "Training";
                    return (
                        <div key={s.source} className="card" style={{ borderColor: isTraining ? 'var(--warning)' : 'var(--ok)' }}>
                            <div className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                                <span style={{ fontSize: 16, color: "var(--text-main)" }}>{s.source}</span>
                                <span className={`badge ${isTraining ? 'warning' : 'ok'}`}>
                                    {isTraining ? 'LEARNING' : 'ACTIVE'}
                                </span>
                            </div>

                            {isTraining ? (
                                <div>
                                    <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 8 }}>
                                        Building Baseline Model... ({s.samples}/{s.required_samples} samples)
                                    </div>
                                    <div style={{ width: '100%', height: 6, background: '#333', borderRadius: 3, overflow: 'hidden' }}>
                                        <div style={{
                                            width: `${s.progress}%`,
                                            height: '100%',
                                            background: 'var(--warning)',
                                            transition: 'width 0.5s ease'
                                        }} />
                                    </div>
                                    <div style={{ textAlign: 'right', fontSize: 10, marginTop: 4, color: 'var(--warning)' }}>
                                        {s.progress}% Complete
                                    </div>
                                </div>
                            ) : (
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: "10px 0" }}>
                                    <div style={{ fontSize: 28 }}>🧠</div>
                                    <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                                        Anomaly Detection is <strong>Online</strong>.<br />
                                        Monitoring behavior deviations.
                                    </div>
                                </div>
                            )}

                            {isAdmin && (
                                <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid rgba(255,255,255,0.05)", textAlign: "right" }}>
                                    <button 
                                        className="btn-ghost btn-danger" 
                                        style={{ fontSize: 11, padding: "6px 12px" }}
                                        onClick={() => handleReset(s.source)}
                                    >
                                        RESET BRAIN
                                    </button>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        )}
      </div>
    </div>
  );
}
