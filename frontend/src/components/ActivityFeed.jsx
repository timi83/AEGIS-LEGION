import React, { useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";

export default function ActivityFeed({ apiBase = "/api", onRefresh }) {
  const { token } = useContext(AuthContext);
  const [source, setSource] = useState("");
  const [etype, setEtype] = useState("");
  const [severity, setSeverity] = useState("low");
  const [status, setStatus] = useState(null);

  async function send() {
    if (!token) {
      setStatus({ msg: "Error: No active session", color: "var(--danger)" });
      return;
    }
    try {
      const payload = { source, event_type: etype, details: "from ui", severity, data: {} };
      const res = await axios.post(`${apiBase}/ingest/`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const rules = res.data.rules_triggered || [];
      setStatus({
        msg: "Sent successfully",
        rules: rules.length > 0 ? JSON.stringify(rules) : "[]",
        color: "var(--success)"
      });
      
      if (onRefresh) onRefresh();
    } catch (e) {
      console.error("ActivityFeed send error:", e);
      setStatus({ msg: "Send failed", color: "var(--danger)" });
    }
  }

  return (
    <div style={{ marginTop: 8 }}>
      <div className="form-row" style={{ flexDirection: 'column', gap: 8 }}>
        <input className="input" value={source} onChange={e => setSource(e.target.value)} placeholder="Source (e.g. firewall)" />
        <input className="input" value={etype} onChange={e => setEtype(e.target.value)} placeholder="Event Type (e.g. login_failed)" />
        <select className="select" value={severity} onChange={e => setSeverity(e.target.value)}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>
      <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
        <button className="btn" onClick={send}>Send</button>
        <button className="btn-ghost" onClick={() => { setSource(""); setEtype(""); setSeverity("low"); setStatus(null); }}>Clear</button>
      </div>
      
      {status && (
        <div style={{ marginTop: 12, padding: 10, background: 'rgba(0,0,0,0.2)', borderRadius: 4, borderLeft: `3px solid ${status.color}` }}>
          <div style={{ color: status.color, fontWeight: 'bold' }}>Status: {status.msg}</div>
          {status.rules && (
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
              rules_triggered: <span style={{ fontFamily: 'monospace', color: 'var(--text-main)' }}>{status.rules}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
