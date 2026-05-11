import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { useSearchParams } from "react-router-dom";
import QuickStats from "./QuickStats";
import ActivityFeed from "./ActivityFeed";
import IncidentTable from "./IncidentTable";
import IncidentModal from "./IncidentModal";
import ThreatTrendChart from "./ThreatTrendChart";

import Navbar from "./Navbar";
import { AuthContext } from "../context/AuthContext";
import { EventsContext } from "../context/EventsContext";

import { Link } from "react-router-dom";

function MLStatusCard({ apiBase, token }) {
  const [statuses, setStatuses] = useState([]);

  useEffect(() => {
    if (!token) return;
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`${apiBase}/servers/ml/status`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStatuses(res.data);
      } catch (e) {
        console.error("Failed to load ML Status", e);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, [token, apiBase]);

  return (
    <div className="card">
      <div className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>ML Brain Monitor</span>
        <Link to="/ml" style={{ fontSize: 11, color: 'var(--accent)', textDecoration: 'none', padding: '4px 8px', border: '1px solid var(--accent)', borderRadius: 4 }}>
          Manage Models →
        </Link>
      </div>
      <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
        {statuses.length === 0 ? (
          <div style={{ fontSize: 12, color: 'var(--muted)', fontStyle: 'italic', textAlign: "center", padding: "10px 0" }}>
            No ML models active yet. Waiting for server telemetry...
          </div>
        ) : (
          statuses.map(s => {
            const isTraining = s.mode === "Training";
            return (
              <div key={s.source} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12, padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: isTraining ? 'var(--warning)' : 'var(--ok)' }} />
                  <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{s.source}</span>
                </div>
                <div style={{ color: "var(--muted)" }}>
                  {isTraining ? <span style={{ color: "var(--warning)" }}>Training ({s.progress}%)</span> : <span style={{ color: "var(--ok)" }}>Trained (Active)</span>}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
export default function Dashboard({ apiBase = "/api" }) {
  const { token, user } = useContext(AuthContext);
  const [searchParams, setSearchParams] = useSearchParams();
  const [incidents, setIncidents] = useState([]);
  const [statusMsg, setStatusMsg] = useState("Ready");
  const [quickStatus, setQuickStatus] = useState(""); // New state for floating button
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState("dashboard");
  const [eventType, setEventType] = useState("manual_test");
  const [severity, setSeverity] = useState("low");
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [visibleCount, setVisibleCount] = useState(10);

  // Handle URL params for deep linking
  useEffect(() => {
    if (!token) return;
    const incId = searchParams.get("incidentId"); // e.g. ?incidentId=123

    if (incId) {
      // Fetch specific incident to ensure we have it even if not in list yet
      axios.get(`${apiBase}/incidents/${incId}`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(res => {
        setSelectedIncident(res.data);
        // Optional: clear param if you want URL to be clean
        // setSearchParams({}); 
      }).catch(e => console.error("Failed to load deep-linked incident", e));
    }
  }, [token, searchParams]);

  async function fetchIncidents() {
    if (!token) return; // Wait for token
    setLoading(true);
    try {
      const res = await axios.get(`${apiBase}/incidents/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const payload = res.data;

      let arr = [];
      if (Array.isArray(payload)) arr = payload;
      else if (Array.isArray(payload?.incidents)) arr = payload.incidents;
      else arr = [];

      setIncidents(arr);
      setStatusMsg("System Updated");
    } catch (err) {
      console.error("fetchIncidents error:", err);
      if (err.response?.status === 401) {
        setStatusMsg("Session Expired");
      } else {
        setStatusMsg(`Error: ${err.response?.status || "Network"}`);
      }
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  }

  // SSE: subscribe to real-time events from Context
  const { lastEvent } = useContext(EventsContext);

  useEffect(() => {
    if (token) {
      fetchIncidents();
      const id = setInterval(fetchIncidents, 30000); // 30s backup poll
      return () => clearInterval(id);
    }
  }, [token]);

  // React to Global Events
  useEffect(() => {
    if (!lastEvent) return;
    const payload = lastEvent;
    console.log("Dashboard received event:", payload.type, payload);

    // Logic from previous SSE handler
    // If an incident was created, update incidents list.
    if (payload.incident) {
      setIncidents((prev) => {
        // avoid duplicates by event_id or id
        const exists = prev.some((i) => i.event_id === payload.incident.event_id || i.id == payload.incident.id);
        if (exists) {
          // update existing
          return prev.map(i => (i.event_id === payload.incident.event_id ? { ...i, ...payload.incident } : i));
        }
        // prepend new incident for visibility
        return [payload.incident, ...prev].slice(0, 200); // keep reasonable max
      });
      setStatusMsg("New Incident Detected");
    }

    if (payload.type === "status_update") {
      setIncidents((prev) =>
        prev.map((i) =>
          i.id == payload.incident_id ? { ...i, status: payload.new_status } : i
        )
      );
      // Also update selected incident if open
      if (selectedIncident && selectedIncident.id == payload.incident_id) {
        setSelectedIncident(prev => ({ ...prev, status: payload.new_status }));
      }
      setStatusMsg(`Incident #${payload.incident_id} Updated`);
    }

    if (payload.type === "note_added") {
      let noteText = payload.note;
      if (typeof payload.note === 'object') {
        const n = payload.note;
        noteText = `[${n.timestamp}] ${n.user}: ${n.content}`;
      }

      setIncidents((prev) =>
        prev.map((i) =>
          i.id == payload.incident_id
            ? { ...i, response_notes: (i.response_notes || "") + `\n${noteText}` }
            : i
        )
      );
      // Also update selected incident if open (though Modal fetches its own, this keeps legacy props synced)
      if (selectedIncident && selectedIncident.id == payload.incident_id) {
        setSelectedIncident(prev => ({
          ...prev,
          response_notes: (prev.response_notes || "") + `\n${noteText}`
        }));
      }
      // setStatusMsg(`Note added to #${payload.incident_id}`); // Optional, can be noisy
    }

    if (payload.type === "assignment_update") {
      console.log("Processing assignment update for", payload.incident_id);
      setIncidents(prev => prev.map(i =>
        i.id == payload.incident_id
          ? { ...i, assignees: payload.assignees }
          : i
      ));
      if (selectedIncident && selectedIncident.id == payload.incident_id) {
        setSelectedIncident(prev => ({ ...prev, assignees: payload.assignees }));
      }
      setStatusMsg(`Assignments Updated #${payload.incident_id}`);
    }

  }, [lastEvent]);

  // Scroll to bottom when modal opens
  useEffect(() => {
    if (selectedIncident) {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
  }, [selectedIncident]);

  async function sendTestEvent() {
    try {
      const payload = {
        source: source,
        event_type: eventType,
        details: "Manual test from frontend",
        severity: severity,
        data: { note: "ui-test" }
      };
      const res = await axios.post(`${apiBase}/ingest/`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatusMsg("Event Ingested: " + (res?.data?.message || "OK"));
      fetchIncidents();
    } catch (err) {
      setStatusMsg("Ingest Failed");
    }
  }

  async function sendQuickEvent() {
    try {
      setQuickStatus("Sending...");
      const payload = {
        source: "dashboard",
        event_type: "quick_test",
        details: "Quick test from floating button",
        severity: "low",
        data: { note: "quick-ui-test" }
      };
      const res = await axios.post(`${apiBase}/ingest/`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setQuickStatus("Event Sent ✓");
      fetchIncidents();
      setTimeout(() => setQuickStatus(""), 3000); // Clear after 3s
    } catch (err) {
      setQuickStatus("Failed ✗");
      setTimeout(() => setQuickStatus(""), 3000);
    }
  }

  const incidentsList = Array.isArray(incidents) ? incidents : [];

  return (
    <div className="app-wrapper">
      <Navbar />

      <div className="container animate-fade-in">
        <div className="grid" style={{ gridTemplateColumns: "1fr 350px", alignItems: "start" }}>

          {/* Main Column */}
          <div className="grid" style={{ gap: 24 }}>
            <QuickStats incidents={incidentsList} statusMsg={statusMsg} />

            <div className="card">
              <div className="header" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Threat Trends</span>
                <span className="badge low">Live</span>
              </div>
              <ThreatTrendChart incidents={incidentsList} />
            </div>

            <div className="card">
              <div className="header">Recent Incidents</div>
              <IncidentTable incidents={incidentsList.slice(0, visibleCount)} onView={setSelectedIncident} apiBase={apiBase} />

              {visibleCount < incidentsList.length && (
                <div style={{ textAlign: 'center', padding: '10px 0' }}>
                  <button
                    className="btn secondary"
                    onClick={() => {
                      if (visibleCount === 10) setVisibleCount(30);
                      else setVisibleCount(incidentsList.length);
                    }}
                    style={{ fontSize: 12, padding: '6px 16px' }}
                  >
                    {visibleCount === 10 ? 'View More (20)' : 'View All'}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="grid" style={{ gap: 24 }}>
            {/* New ML Status Card */}
            <MLStatusCard apiBase={apiBase} token={token} user={user} />

            <div className="card">
              <div className="header">Activity Feed / Manual Ingest</div>
              <ActivityFeed apiBase={apiBase} onRefresh={fetchIncidents} />
            </div>
          </div>

        </div>
      </div>

      {/* Floating Action Button Container */}
      <div style={{
        position: 'fixed',
        bottom: 30,
        right: 30,
        zIndex: 100,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-end',
        gap: 8
      }}>
        <button
          className="btn"
          onClick={sendQuickEvent}
          style={{
            opacity: 0.9,
            boxShadow: '0 0 20px rgba(0, 255, 157, 0.2)',
            fontSize: 12,
            padding: '10px 20px',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            fontWeight: 700
          }}
          onMouseEnter={e => e.target.style.opacity = 1}
          onMouseLeave={e => e.target.style.opacity = 0.9}
        >
          Send Test Event
        </button>
        {quickStatus && (
          <div style={{
            color: 'var(--primary)',
            fontSize: 11,
            fontWeight: 600,
            textShadow: '0 0 5px rgba(0, 255, 157, 0.5)',
            animation: 'fadeIn 0.3s ease-out',
            background: 'rgba(0,0,0,0.6)',
            padding: '4px 8px',
            borderRadius: 4,
            backdropFilter: 'blur(4px)'
          }}>
            {quickStatus}
          </div>
        )}
      </div>

      {selectedIncident && (
        <IncidentModal
          incident={selectedIncident}
          onClose={() => setSelectedIncident(null)}
          apiBase={apiBase}
        />
      )}
    </div>
  );
}
