import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";

export default function QuickStats({ incidents, statusMsg, apiBase = "/api" }) {
  const { token } = useContext(AuthContext);
  const [servers, setServers] = useState([]);

  useEffect(() => {
    if (!token) return;
    const fetchServers = async () => {
      try {
        const res = await axios.get(`${apiBase}/servers`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setServers(res.data);
      } catch (e) {
        console.error("Failed to load servers", e);
      }
    };
    
    // Fetch immediately and poll every 15s to keep it fresh
    fetchServers();
    const interval = setInterval(fetchServers, 15000); 
    return () => clearInterval(interval);
  }, [token, apiBase]);

  const activeServers = servers.filter(s => s.status !== "offline").length;
  const offlineServers = servers.length - activeServers;

  return (
    <div className="card" style={{marginBottom:12}}>
      <h3 className="header" style={{color:"var(--muted)"}}>Quick Stats</h3>
      <div style={{marginTop:10, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16}}>
        
        {/* Incident Stats */}
        <div style={{ paddingRight: 16, borderRight: '1px solid rgba(255,255,255,0.1)' }}>
            <div style={{ marginBottom: 4 }}>Total incidents: <strong style={{ color: "var(--text-main)" }}>{incidents.length}</strong></div>
            <div style={{ marginBottom: 4, color: "var(--muted)" }}>Open: <span style={{ color: "#fff" }}>{incidents.filter(i=>i.status?.toLowerCase() === "open").length}</span></div>
            <div style={{ color: "var(--muted)" }}>High severity: <span style={{ color: "var(--error)" }}>{incidents.filter(i=>i.severity?.toLowerCase() === "high").length}</span></div>
        </div>

        {/* Server Stats */}
        <div style={{ paddingLeft: 8 }}>
            <div style={{ marginBottom: 4 }}>Total Servers: <strong style={{ color: "var(--text-main)" }}>{servers.length}</strong></div>
            <div style={{ marginBottom: 4, color: "var(--muted)" }}>
              Active: <span style={{ color: activeServers > 0 ? "var(--ok)" : "#fff", fontWeight: 600 }}>{activeServers}</span>
            </div>
            <div style={{ color: "var(--muted)" }}>
              Offline: <span style={{ color: offlineServers > 0 ? "var(--error)" : "#fff" }}>{offlineServers}</span>
            </div>
        </div>

        {/* System Status */}
        <div style={{ gridColumn: "1 / -1", marginTop: 8, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.05)', color: "var(--muted)", fontSize: 12, display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: statusMsg.includes("Error") ? "var(--error)" : "var(--ok)" }}></div>
          {statusMsg}
        </div>
      </div>
    </div>
  );
}
