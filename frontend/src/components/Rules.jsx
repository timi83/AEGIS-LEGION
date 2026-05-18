// frontend/src/components/Rules.jsx
import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";
import Navbar from "./Navbar";

export default function Rules({ apiBase = "/api" }) {
    const { token } = useContext(AuthContext);
    const [rules, setRules] = useState([]);
    const [servers, setServers] = useState([]);
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [severity, setSeverity] = useState("medium");
    const [field, setField] = useState("event_type");
    const [op, setOp] = useState("equals");
    const [value, setValue] = useState("");
    const [status, setStatus] = useState("");
    const [targetServer, setTargetServer] = useState("");
    const [showHelp, setShowHelp] = useState(false);

    async function fetchRules() {
        if (!token) return;
        try {
            const res = await axios.get(`${apiBase}/rules/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setRules(res.data || []);
        } catch (e) {
            console.error("fetchRules error", e);
            setStatus("Failed to fetch rules");
        }
    }

    async function fetchServers() {
        if (!token) return;
        try {
            const res = await axios.get(`${apiBase}/servers/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setServers(res.data || []);
        } catch (e) {
            console.error("fetchServers error", e);
        }
    }

    useEffect(() => {
        fetchRules();
        fetchServers();
    }, [token]);

    async function createRule(e) {
        e.preventDefault();
        if (!token) return;
        setStatus("Creating rule...");
        try {
            const payload = {
                name,
                description,
                severity,
                target_server: targetServer || null,
                conditions: [{ field, op, value }]
            };
            const res = await axios.post(`${apiBase}/rules/`, payload, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStatus("Rule created");
            // reset form
            setName(""); setDescription(""); setValue(""); setField("event_type"); setOp("equals"); setTargetServer("");
            fetchRules();
        } catch (err) {
            console.error("createRule error", err);
            setStatus("Failed to create rule");
        }
    }

    async function deleteRule(id) {
        if (!token) return;
        if (!confirm("Delete rule?")) return;
        try {
            await axios.delete(`${apiBase}/rules/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStatus("Rule deleted");
            fetchRules();
        } catch (e) {
            console.error(e);
            setStatus("Failed to delete");
        }
    }

    return (
        <div className="app-wrapper">
            <Navbar />
            <div className="container animate-fade-in">
                <div className="card" style={{ padding: 24 }}>
                    <h3 className="header">Rule Management</h3>
                    <div style={{ marginTop: 24 }}>
                        <form onSubmit={createRule} className="form-grid" style={{ marginBottom: 32 }}>
                            <div className="form-grid" style={{ gridColumn: "1 / -1" }}>
                                <input placeholder="Rule name" value={name} onChange={e => setName(e.target.value)} className="input" required />
                                <select value={severity} onChange={e => setSeverity(e.target.value)} className="select">
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
                                </select>
                                <select value={targetServer} onChange={e => setTargetServer(e.target.value)} className="select" style={{ gridColumn: "1 / -1" }}>
                                    <option value="">Apply to All Servers (Global)</option>
                                    {servers.map(s => (
                                        <option key={s.hostname} value={s.hostname}>Apply only to {s.hostname}</option>
                                    ))}
                                </select>
                            </div>

                            <input placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} className="input" style={{ gridColumn: "1 / -1" }} />

                            <div style={{ gridColumn: "1 / -1", display: "flex", gap: 8, alignItems: "center" }}>
                                <span style={{ color: "var(--text-muted)", fontSize: 14 }}>Condition:</span>
                                <input
                                    list="field-suggestions"
                                    placeholder="field (e.g. event_type)"
                                    value={field}
                                    onChange={e => setField(e.target.value)}
                                    className="input"
                                    style={{ flex: 1 }}
                                />
                                <datalist id="field-suggestions">
                                    <option value="event_type" />
                                    <option value="severity" />
                                    <option value="source" />
                                    <option value="data.cpu" />
                                    <option value="data.ram" />
                                    <option value="data.disk_write_mb" />
                                    <option value="data.disk_read_mb" />
                                    <option value="data.net_in_mb" />
                                    <option value="data.net_out_mb" />
                                    <option value="data.net_connections" />
                                    <option value="data.top_process" />
                                    <option value="data.fail_count" />
                                    <option value="data.user" />
                                    <option value="data.path" />
                                </datalist>
                                <select value={op} onChange={e => setOp(e.target.value)} className="select" style={{ width: 100 }}>
                                    <option value="equals">equals</option>
                                    <option value="contains">contains</option>
                                    <option value="gt">gt</option>
                                    <option value="lt">lt</option>
                                </select>
                                <input placeholder="value" value={value} onChange={e => setValue(e.target.value)} className="input" style={{ flex: 1, minWidth: 80 }} />
                            </div>

                            <div style={{ gridColumn: "1 / -1", display: "flex", gap: 12, marginTop: 12 }}>
                                <button type="submit" className="btn">Create Rule</button>
                                <button type="button" className="btn-ghost" onClick={() => { setName(""); setDescription(""); setValue(""); setField("event_type"); setOp("equals"); setTargetServer(""); }}>Clear</button>
                            </div>
                        </form>
                        <div style={{ color: "var(--accent)", marginBottom: 12, fontSize: 14 }}>{status}</div>
                        <h4 className="header" style={{ fontSize: 18 }}>Existing Rules</h4>
                        {rules.length === 0 ? <div style={{ color: "var(--text-muted)" }}>No rules defined.</div> : (
                            <div style={{ marginTop: 16, display: "grid", gap: 12 }}>
                                {rules.map(r => (
                                    <div key={r.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 16, background: "rgba(255,255,255,0.02)" }}>
                                        <div>
                                            <div style={{ fontWeight: 600, color: "var(--text-main)", display: "flex", alignItems: "center", gap: 8 }}>
                                                {r.name}
                                                <span className={`badge ${r.severity}`}>{r.severity}</span>
                                                {r.target_server && (
                                                    <span style={{ fontSize: 10, background: 'rgba(0, 255, 157, 0.1)', color: 'var(--ok)', padding: '2px 6px', borderRadius: 4, border: '1px solid var(--ok)' }}>
                                                        🎯 {r.target_server}
                                                    </span>
                                                )}
                                                {!r.target_server && (
                                                    <span style={{ fontSize: 10, background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', padding: '2px 6px', borderRadius: 4, border: '1px solid rgba(255,255,255,0.1)' }}>
                                                        🌐 Global
                                                    </span>
                                                )}
                                            </div>
                                            <div style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 4 }}>{r.description}</div>
                                            <div style={{ marginTop: 6, fontSize: 12, fontFamily: "var(--font-mono)", color: "var(--primary)" }}>
                                                {JSON.stringify(r.conditions)}
                                            </div>
                                        </div>
                                        <div>
                                            <button className="btn-ghost btn-danger" onClick={() => deleteRule(r.id)} style={{ padding: "6px 12px", fontSize: 12 }}>Delete</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Help Toggle & Modal */}
                <div style={{ marginTop: 24, display: 'flex', justifyContent: 'center' }}>
                    <button
                        onClick={() => setShowHelp(!showHelp)}
                        style={{
                            width: 32, height: 32, borderRadius: '50%', border: '1px solid #444',
                            background: showHelp ? 'var(--accent)' : 'transparent',
                            color: showHelp ? '#000' : '#888',
                            cursor: 'pointer', transition: 'all 0.3s ease',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: 14, fontWeight: 700
                        }}
                        title="Help: Field naming guide"
                    >
                        ?
                    </button>
                </div>

                {showHelp && (
                    <div style={{
                        marginTop: 16, padding: 24,
                        border: '1px solid #333', borderRadius: 8,
                        background: 'var(--bg-card, rgba(0,0,0,0.4))',
                        animation: 'fadeIn 0.5s ease',
                        color: 'var(--text-muted)',
                        fontSize: 13,
                        lineHeight: 1.6
                    }}>
                        <h4 style={{ margin: '0 0 16px 0', fontSize: 16, color: 'var(--accent)' }}>Rule Creation Guide</h4>
                        
                        <div style={{ marginBottom: 20 }}>
                            <strong style={{ color: '#fff', fontSize: 14 }}>1. How Rules Work</strong>
                            <p style={{ marginTop: 4 }}>
                                When your agent sends an event, it includes a JSON payload. A Rule acts as an automated tripwire: 
                                <em>"If the payload contains X, and X is greater than Y, create an Incident."</em><br />
                                Use <strong>Dot Notation</strong> to target specific pieces of data (e.g., <code>data.cpu</code>).
                            </p>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 20 }}>
                            <div>
                                <strong style={{ color: '#fff', fontSize: 14 }}>2. Available Metric Fields</strong>
                                <div style={{ marginTop: 8 }}>
                                    <strong style={{ color: '#ddd' }}>Top-Level Fields:</strong><br />
                                    • <code>event_type</code>: e.g., system_heartbeat, login_failed<br />
                                    • <code>source</code>: Server hostname<br />
                                    <br />
                                    <strong style={{ color: '#ddd' }}>Universal Data:</strong><br />
                                    • <code>data.ip</code>: IP address<br />
                                    • <code>data.os</code>: Operating System<br />
                                    <br />
                                    <strong style={{ color: '#ddd' }}>Hardware Metrics (system_heartbeat):</strong><br />
                                    • <code>data.cpu</code> / <code>data.ram</code> (0-100)<br />
                                    • <code>data.disk_read_mb</code> / <code>data.disk_write_mb</code><br />
                                    • <code>data.net_in_mb</code> / <code>data.net_out_mb</code><br />
                                    • <code>data.net_connections</code>: Active network connections<br />
                                    • <code>data.top_process</code>: Highest CPU process name<br />
                                    <br />
                                    <strong style={{ color: '#ddd' }}>Threat Specific:</strong><br />
                                    • <code>data.fail_count</code> / <code>data.user</code> (login_failed)<br />
                                    • <code>data.path</code> / <code>data.hash</code> (malware_detected)<br />
                                </div>
                            </div>
                            
                            <div>
                                <strong style={{ color: '#fff', fontSize: 14 }}>3. Operators</strong>
                                <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                                    <li><code>gt</code>: Greater Than (Best for numeric spikes)</li>
                                    <li><code>lt</code>: Less Than (Best for sudden drops)</li>
                                    <li><code>equals</code>: Exact Match (Best for strings)</li>
                                    <li><code>contains</code>: Substring Match (Best for paths/names)</li>
                                </ul>

                                <strong style={{ color: '#fff', fontSize: 14, display: 'block', marginTop: 20 }}>4. Real-World Examples</strong>
                                <div style={{ marginTop: 8, background: 'rgba(0,0,0,0.3)', padding: 12, borderRadius: 6 }}>
                                    <strong style={{ color: 'var(--primary)' }}>A. Crypto-Miner (High CPU)</strong><br />
                                    Field: <code>data.cpu</code> | Op: <code>gt</code> | Value: <code>95</code>
                                    <hr style={{ border: 'none', borderTop: '1px solid #333', margin: '8px 0' }} />
                                    
                                    <strong style={{ color: 'var(--primary)' }}>B. Data Exfiltration (Massive Upload)</strong><br />
                                    Field: <code>data.net_out_mb</code> | Op: <code>gt</code> | Value: <code>500</code>
                                    <hr style={{ border: 'none', borderTop: '1px solid #333', margin: '8px 0' }} />
                                    
                                    <strong style={{ color: 'var(--primary)' }}>C. Ransomware (High Disk Writes)</strong><br />
                                    Cond 1: <code>event_type</code> | <code>equals</code> | <code>system_heartbeat</code><br />
                                    Cond 2: <code>data.disk_write_mb</code> | <code>gt</code> | <code>1000</code>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div >
        </div >
    );
}
