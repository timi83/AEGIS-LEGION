// frontend/src/components/Rules.jsx
import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";
import Navbar from "./Navbar";

export default function Rules({ apiBase = "/api" }) {
    const { token } = useContext(AuthContext);
    const [rules, setRules] = useState([]);
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [severity, setSeverity] = useState("medium");
    const [field, setField] = useState("event_type");
    const [op, setOp] = useState("equals");
    const [value, setValue] = useState("");
    const [status, setStatus] = useState("");
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

    useEffect(() => {
        fetchRules();
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
                conditions: [{ field, op, value }]
            };
            const res = await axios.post(`${apiBase}/rules/`, payload, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStatus("Rule created");
            // reset form
            setName(""); setDescription(""); setValue(""); setField("event_type"); setOp("equals");
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
                        <form onSubmit={createRule} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 32 }}>
                            <div style={{ gridColumn: "1 / -1", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                                <input placeholder="Rule name" value={name} onChange={e => setName(e.target.value)} className="input" required />
                                <select value={severity} onChange={e => setSeverity(e.target.value)} className="select">
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
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
                                    <option value="data.username" />
                                    <option value="data.ip_address" />
                                </datalist>
                                <select value={op} onChange={e => setOp(e.target.value)} className="select" style={{ width: 100 }}>
                                    <option value="equals">equals</option>
                                    <option value="contains">contains</option>
                                    <option value="gt">gt</option>
                                    <option value="lt">lt</option>
                                </select>
                                <input placeholder="value" value={value} onChange={e => setValue(e.target.value)} className="input" style={{ flex: 1 }} />
                            </div>

                            <div style={{ gridColumn: "1 / -1", display: "flex", gap: 12, marginTop: 12 }}>
                                <button type="submit" className="btn">Create Rule</button>
                                <button type="button" className="btn-ghost" onClick={() => { setName(""); setDescription(""); setValue(""); setField("event_type"); setOp("equals"); }}>Clear</button>
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
                        marginTop: 16, padding: 16,
                        border: '1px dashed #444', borderRadius: 8,
                        background: 'rgba(0,0,0,0.2)',
                        animation: 'fadeIn 0.5s ease'
                    }}>
                        <h4 style={{ margin: '0 0 12px 0', fontSize: 14, color: 'var(--accent)' }}>Rule Creation Guide</h4>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                            <div>
                                <strong style={{ color: '#fff' }}>Metric Fields:</strong><br />
                                Agent metrics are nested in <code>data</code>.<br />
                                • CPU: <code>data.cpu</code> (0-100)<br />
                                • RAM: <code>data.ram</code> (0-100)<br />
                                • Disk: <code>data.disk_write_mb</code>
                            </div>
                            <div>
                                <strong style={{ color: '#fff' }}>Operators:</strong><br />
                                • <code>gt</code>: Greater Than<br />
                                • <code>lt</code>: Less Than<br />
                                • <code>contains</code>: Substring Match<br />
                                • <code>equals</code>: Exact Match
                            </div>
                        </div>
                    </div>
                )}
            </div >
        </div >
    );
}
