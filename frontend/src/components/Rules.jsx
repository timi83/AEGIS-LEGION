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
            <div className="container animate-fade-in" style={{ padding: '16px' }}>
                <div className="card" style={{ padding: '16px 16px 24px', overflow: 'hidden' }}>
                    <h3 className="header">Rule Management</h3>
                    <div style={{ marginTop: 20 }}>
                        <form onSubmit={createRule} style={{ marginBottom: 28 }}>
                            {/* Row 1: Name + Severity */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 10, marginBottom: 10 }}>
                                <input placeholder="Rule name" value={name} onChange={e => setName(e.target.value)} className="input" required />
                                <select value={severity} onChange={e => setSeverity(e.target.value)} className="select" style={{ minWidth: 90 }}>
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
                                </select>
                            </div>

                            {/* Row 2: Server target */}
                            <select value={targetServer} onChange={e => setTargetServer(e.target.value)} className="select" style={{ width: '100%', marginBottom: 10 }}>
                                <option value="">Apply to All Servers (Global)</option>
                                {servers.map(s => (
                                    <option key={s.hostname} value={s.hostname}>Apply only to {s.hostname}</option>
                                ))}
                            </select>

                            {/* Row 3: Description */}
                            <input placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} className="input" style={{ width: '100%', marginBottom: 10, boxSizing: 'border-box' }} />

                            {/* Condition Builder — stacked on mobile */}
                            <div style={{ marginBottom: 12 }}>
                                <span style={{ color: "var(--text-muted)", fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.5px', display: 'block', marginBottom: 8 }}>Condition</span>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 8 }}>
                                    <input
                                        list="field-suggestions"
                                        placeholder="Field (e.g. data.cpu)"
                                        value={field}
                                        onChange={e => setField(e.target.value)}
                                        className="input"
                                        style={{ width: '100%', boxSizing: 'border-box' }}
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
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                                        <select value={op} onChange={e => setOp(e.target.value)} className="select">
                                            <option value="equals">equals</option>
                                            <option value="contains">contains</option>
                                            <option value="gt">gt (&gt;)</option>
                                            <option value="lt">lt (&lt;)</option>
                                        </select>
                                        <input placeholder="Value" value={value} onChange={e => setValue(e.target.value)} className="input" style={{ width: '100%', boxSizing: 'border-box' }} />
                                    </div>
                                </div>
                            </div>

                            {/* Action buttons */}
                            <div style={{ display: 'flex', gap: 10 }}>
                                <button type="submit" className="btn" style={{ flex: 1 }}>Create Rule</button>
                                <button type="button" className="btn-ghost" style={{ flex: 1 }} onClick={() => { setName(""); setDescription(""); setValue(""); setField("event_type"); setOp("equals"); setTargetServer(""); }}>Clear</button>
                            </div>
                        </form>

                        <div style={{ color: "var(--accent)", marginBottom: 12, fontSize: 14 }}>{status}</div>
                        <h4 className="header" style={{ fontSize: 18 }}>Existing Rules</h4>
                        {rules.length === 0 ? <div style={{ color: "var(--text-muted)" }}>No rules defined.</div> : (
                            <div style={{ marginTop: 16, display: "grid", gap: 12 }}>
                                {rules.map(r => (
                                    <div key={r.id} className="card" style={{ padding: 16, background: "rgba(255,255,255,0.02)", overflow: 'hidden' }}>
                                        {/* Title row: wraps naturally */}
                                        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                                            <span style={{ fontWeight: 600, color: "var(--text-main)" }}>{r.name}</span>
                                            <span className={`badge ${r.severity}`}>{r.severity}</span>
                                            {r.target_server ? (
                                                <span style={{ fontSize: 10, background: 'rgba(0, 255, 157, 0.1)', color: 'var(--ok)', padding: '2px 6px', borderRadius: 4, border: '1px solid var(--ok)' }}>
                                                    🎯 {r.target_server}
                                                </span>
                                            ) : (
                                                <span style={{ fontSize: 10, background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', padding: '2px 6px', borderRadius: 4, border: '1px solid rgba(255,255,255,0.1)' }}>
                                                    🌐 Global
                                                </span>
                                            )}
                                        </div>
                                        <div style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 6 }}>{r.description}</div>
                                        <div style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--primary)", wordBreak: "break-word", whiteSpace: "pre-wrap", background: "rgba(0,0,0,0.25)", padding: 8, borderRadius: 4, overflowX: 'auto' }}>
                                            {JSON.stringify(r.conditions, null, 2)}
                                        </div>
                                        <div style={{ marginTop: 10 }}>
                                            <button className="btn-ghost btn-danger" onClick={() => deleteRule(r.id)} style={{ padding: "8px 16px", fontSize: 12, width: '100%' }}>Delete</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Help Toggle */}
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
                        marginTop: 16, padding: '16px',
                        border: '1px solid #333', borderRadius: 8,
                        background: 'var(--bg-card, rgba(0,0,0,0.4))',
                        animation: 'fadeIn 0.5s ease',
                        color: 'var(--text-muted)',
                        fontSize: 13,
                        lineHeight: 1.6,
                        overflow: 'hidden'
                    }}>
                        <h4 style={{ margin: '0 0 16px 0', fontSize: 16, color: 'var(--accent)' }}>Rule Creation Guide</h4>
                        
                        <div style={{ marginBottom: 20 }}>
                            <strong style={{ color: '#fff', fontSize: 14 }}>1. How Rules Work</strong>
                            <p style={{ marginTop: 4 }}>
                                When your agent sends an event, it includes a JSON payload. A Rule acts as an automated tripwire: 
                                <em>"If the payload contains X, and X is greater than Y, create an Incident."</em><br />
                                Use <strong>Dot Notation</strong> to target specific data (e.g., <code>data.cpu</code>).
                            </p>
                        </div>

                        {/* Single column on mobile, two on desktop */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 24, marginBottom: 20 }}>
                            <div>
                                <strong style={{ color: '#fff', fontSize: 14 }}>2. Available Fields</strong>
                                <div style={{ marginTop: 8 }}>
                                    <strong style={{ color: '#ddd' }}>Top-Level:</strong><br />
                                    • <code>event_type</code>: e.g., system_heartbeat<br />
                                    • <code>source</code>: Server hostname<br />
                                    <br />
                                    <strong style={{ color: '#ddd' }}>Universal:</strong><br />
                                    • <code>data.ip</code> / <code>data.os</code><br />
                                    <br />
                                    <strong style={{ color: '#ddd' }}>Hardware:</strong><br />
                                    • <code>data.cpu</code> / <code>data.ram</code><br />
                                    • <code>data.disk_read_mb</code> / <code>data.disk_write_mb</code><br />
                                    • <code>data.net_in_mb</code> / <code>data.net_out_mb</code><br />
                                    • <code>data.net_connections</code><br />
                                    • <code>data.top_process</code><br />
                                    <br />
                                    <strong style={{ color: '#ddd' }}>Threat:</strong><br />
                                    • <code>data.fail_count</code> / <code>data.user</code><br />
                                    • <code>data.path</code> / <code>data.hash</code><br />
                                </div>
                            </div>
                            
                            <div>
                                <strong style={{ color: '#fff', fontSize: 14 }}>3. Operators</strong>
                                <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                                    <li><code>gt</code>: Greater Than</li>
                                    <li><code>lt</code>: Less Than</li>
                                    <li><code>equals</code>: Exact Match</li>
                                    <li><code>contains</code>: Substring Match</li>
                                </ul>

                                <strong style={{ color: '#fff', fontSize: 14, display: 'block', marginTop: 16 }}>4. Examples</strong>
                                <div style={{ marginTop: 8, background: 'rgba(0,0,0,0.3)', padding: 12, borderRadius: 6, fontSize: 12 }}>
                                    <strong style={{ color: 'var(--primary)' }}>Crypto-Miner</strong><br />
                                    <code>data.cpu</code> → <code>gt</code> → <code>95</code>
                                    <hr style={{ border: 'none', borderTop: '1px solid #333', margin: '8px 0' }} />
                                    <strong style={{ color: 'var(--primary)' }}>Data Exfil</strong><br />
                                    <code>data.net_out_mb</code> → <code>gt</code> → <code>500</code>
                                    <hr style={{ border: 'none', borderTop: '1px solid #333', margin: '8px 0' }} />
                                    <strong style={{ color: 'var(--primary)' }}>Ransomware</strong><br />
                                    <code>data.disk_write_mb</code> → <code>gt</code> → <code>1000</code>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
