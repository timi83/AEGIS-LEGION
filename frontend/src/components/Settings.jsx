import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import Navbar from './Navbar';
import { AuthContext } from '../context/AuthContext';
import ServerAccessModal from './ServerAccessModal'; // Import

export default function Settings() {
    const { token, refreshUser } = useContext(AuthContext);
    const [user, setUser] = useState(null);
    const [apiKey, setApiKey] = useState('');
    const [servers, setServers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [copied, setCopied] = useState(false);

    // New Key State
    const [newKey, setNewKey] = useState(null);
    const [countdown, setCountdown] = useState(0);

    // Access Modal State
    const [accessModalServer, setAccessModalServer] = useState(null);

    const renameOrganization = async () => {
        const currentName = user?.organization;
        const newName = prompt("Enter new Organization Name (Changes apply to ALL users):", currentName);
        if (!newName || newName === currentName) return;

        try {
            await axios.put('/api/organization', { name: newName }, { headers: { Authorization: `Bearer ${token}` } });
            alert(`Organization renamed to '${newName}' successfully!`);

            // Optimistic Update
            setUser(prev => ({ ...prev, organization: newName }));
            if (refreshUser) refreshUser();

        } catch (err) {
            alert("Failed to rename organization: " + (err.response?.data?.detail || err.message));
        }
    };

    // Audit Logs
    const [auditLogs, setAuditLogs] = useState([]);

    const [usersList, setUsersList] = useState([]);
    const [newUser, setNewUser] = useState({ username: '', email: '', password: '', role: 'viewer', organization: 'Internal' });

    useEffect(() => {
        fetchData();
    }, [token]);

    const fetchData = async () => {
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const userRes = await axios.get('/api/me', { headers: { Authorization: `Bearer ${token}` } });
            setUser(userRes.data);
            setApiKey(userRes.data.api_key || '');

            const serversRes = await axios.get('/api/servers', { headers: { Authorization: `Bearer ${token}` } });
            setServers(serversRes.data);

            if (userRes.data.role === 'admin') {
                const usersRes = await axios.get('/api/users', { headers: { Authorization: `Bearer ${token}` } });
                setUsersList(usersRes.data);
            }

            // Fetch Audit Logs
            const auditRes = await axios.get('/api/audit-logs', { headers: { Authorization: `Bearer ${token}` } });
            setAuditLogs(auditRes.data);

            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch settings data", err);
            setError(err.response?.data?.detail || "Failed to load settings.");
            setLoading(false);
        }
    };

    const createUser = async (e) => {
        e.preventDefault();
        try {
            await axios.post('/api/users', {
                ...newUser,
                full_name: newUser.username // Default full name
            }, { headers: { Authorization: `Bearer ${token}` } });
            alert("User created successfully!");
            setNewUser({ username: '', email: '', password: '', role: 'viewer', organization: 'Internal' });
            fetchData(); // Refresh list
        } catch (err) {
            alert("Failed to create user: " + (err.response?.data?.detail || err.message));
        }
    };

    const generateApiKey = async () => {
        try {
            const res = await axios.post('/api/generate-api-key', {}, { headers: { Authorization: `Bearer ${token}` } });
            setApiKey(res.data.api_key);

            // Show new key with countdown
            setNewKey(res.data.api_key);
            setCountdown(10);

            const interval = setInterval(() => {
                setCountdown((prev) => {
                    if (prev <= 1) {
                        clearInterval(interval);
                        setNewKey(null);
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);

            fetchData(); // Refresh to show new audit log
        } catch (err) {
            alert("Failed to generate key.");
        }
    };

    const deleteServer = async (id) => {
        if (!window.confirm("Are you sure? This cannot be undone.")) return;
        try {
            await axios.delete(`/api/servers/${id}`, { headers: { Authorization: `Bearer ${token}` } });
            setServers(servers.filter(s => s.id !== id));
        } catch (err) {
            alert("Failed to delete server. You might not be an admin.");
        }
    };

    const renameServer = async (id, currentName) => {
        const newName = prompt("Enter new name:", currentName);
        if (!newName) return;
        try {
            await axios.put(`/api/servers/${id}`, { name: newName }, { headers: { Authorization: `Bearer ${token}` } });
            setServers(servers.map(s => s.id === id ? { ...s, name: newName } : s));
        } catch (err) {
            alert("Failed to rename server.");
        }
    };

    const copyToClipboard = () => {
        const keyToCopy = newKey || apiKey;
        if (!keyToCopy) {
            alert("No key created");
            return;
        }
        navigator.clipboard.writeText(keyToCopy);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (loading) return <div style={{ padding: 20 }}>Loading settings...</div>;

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content-area" style={{ padding: 40 }}>
                <h1 className="title">Command Center Settings</h1>
                {error && <div style={{ color: 'red' }}>{error}</div>}

                <div className="card" style={{ marginBottom: 30 }}>
                    <h2 style={{ fontSize: 20, marginBottom: 15, borderBottom: '1px solid #333', paddingBottom: 10 }}>
                        User Profile
                    </h2>
                    <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr', gap: 10 }}>
                        <div style={{ color: 'var(--muted)' }}>Username:</div>
                        <div>{user?.username}</div>
                        <div style={{ color: 'var(--muted)' }}>Role:</div>
                        <div style={{ textTransform: 'uppercase', color: 'var(--accent)' }}>{user?.role}</div>
                        <div style={{ color: 'var(--muted)' }}>Email:</div>
                        <div>{user?.email || 'N/A'}</div>
                        <div style={{ color: 'var(--muted)', alignSelf: 'center' }}>Organization:</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <div style={{ fontWeight: 'bold' }}>{user?.organization || 'N/A'}</div>
                            {user?.role === 'admin' && (
                                <button
                                    className="btn-ghost"
                                    style={{
                                        fontSize: 10,
                                        padding: '2px 6px',
                                        border: '1px solid #444',
                                        marginLeft: 0
                                    }}
                                    onClick={renameOrganization}
                                >
                                    EDIT
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                {user?.role === 'admin' && (
                    <div className="card" style={{ marginBottom: 30 }}>
                        <h2 style={{ fontSize: 20, marginBottom: 15, borderBottom: '1px solid #333', paddingBottom: 10 }}>
                            User Management (Admin Only)
                        </h2>

                        <div style={{ marginBottom: 20 }}>
                            <h3 style={{ fontSize: 16, marginBottom: 10, color: 'var(--accent)' }}>Create New User</h3>
                            <form onSubmit={createUser} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr auto', gap: 10, alignItems: 'end' }}>
                                <div>
                                    <label style={{ fontSize: 12, color: 'var(--muted)' }}>Username</label>
                                    <input className="input" required value={newUser.username} onChange={e => setNewUser({ ...newUser, username: e.target.value })} />
                                </div>
                                <div>
                                    <label style={{ fontSize: 12, color: 'var(--muted)' }}>Email</label>
                                    <input className="input" type="email" required value={newUser.email} onChange={e => setNewUser({ ...newUser, email: e.target.value })} />
                                </div>
                                <div>
                                    <label style={{ fontSize: 12, color: 'var(--muted)' }}>Password</label>
                                    <input className="input" type="password" required value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} />
                                </div>
                                <div>
                                    <label style={{ fontSize: 12, color: 'var(--muted)' }}>Role</label>
                                    <select className="input" value={newUser.role} onChange={e => setNewUser({ ...newUser, role: e.target.value })}>
                                        <option value="viewer">Viewer</option>
                                        <option value="analyst">Analyst</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>
                                <button className="btn" type="submit">Create</button>
                            </form>
                        </div>

                        <h3 style={{ fontSize: 16, marginBottom: 10, color: 'var(--muted)' }}>Existing Users</h3>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ textAlign: 'left', color: 'var(--muted)', fontSize: 12 }}>
                                    <th style={{ padding: 5 }}>USERNAME</th>
                                    <th style={{ padding: 5 }}>ROLE</th>
                                    <th style={{ padding: 5 }}>EMAIL</th>
                                    <th style={{ padding: 5 }}>ORG</th>
                                    <th style={{ padding: 5 }}>ACTION</th>
                                </tr>
                            </thead>
                            <tbody>
                                {usersList.map(u => (
                                    <tr key={u.id} style={{ borderBottom: '1px solid #222' }}>
                                        <td style={{ padding: 5, fontWeight: 'bold' }}>{u.username}</td>
                                        <td style={{ padding: 5, textTransform: 'uppercase', color: 'var(--accent)' }}>{u.role}</td>
                                        <td style={{ padding: 5 }}>{u.email}</td>
                                        <td style={{ padding: 5 }}>{u.organization}</td>
                                        <td style={{ padding: 5 }}>
                                            {u.id !== user.id && (
                                                <>
                                                    <button
                                                        className="btn-ghost"
                                                        style={{ fontSize: 10, padding: '2px 6px', marginRight: 5, color: 'var(--accent)', borderColor: 'var(--accent)' }}
                                                        onClick={async () => {
                                                            const newPw = prompt(`Enter new password for ${u.username}:`);
                                                            if (!newPw) return;
                                                            try {
                                                                await axios.put(`/api/users/${u.id}/reset-password`, { new_password: newPw }, { headers: { Authorization: `Bearer ${token}` } });
                                                                alert("Password reset successfully.");
                                                            } catch (e) {
                                                                alert("Failed to reset password: " + (e.response?.data?.detail || e.message));
                                                            }
                                                        }}
                                                    >
                                                        RESET PW
                                                    </button>
                                                    <button
                                                        className="btn-ghost btn-danger"
                                                        style={{ fontSize: 10, padding: '2px 6px' }}
                                                        onClick={async () => {
                                                            if (!window.confirm(`Are you sure you want to delete user ${u.username}?`)) return;
                                                            try {
                                                                await axios.delete(`/api/users/${u.id}`, { headers: { Authorization: `Bearer ${token}` } });
                                                                setUsersList(prev => prev.filter(x => x.id !== u.id));
                                                            } catch (e) {
                                                                alert("Failed to delete user: " + (e.response?.data?.detail || e.message));
                                                            }
                                                        }}
                                                    >
                                                        DELETE
                                                    </button>
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                <div className="card" style={{ marginBottom: 30 }}>
                    <h2 style={{ fontSize: 20, marginBottom: 15, borderBottom: '1px solid #333', paddingBottom: 10 }}>
                        API Access
                    </h2>
                    <p style={{ marginBottom: 15, color: 'var(--muted)' }}>
                        Use this key in your <code>agent.py</code> to authenticate your servers.
                    </p>
                    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                        {newKey ? (
                            <div style={{
                                flex: 1,
                                background: 'var(--accent)',
                                color: '#000',
                                padding: '10px',
                                fontWeight: 'bold',
                                textAlign: 'center',
                                borderRadius: 4,
                                fontFamily: 'monospace',
                                fontSize: 16
                            }}>
                                {newKey} (Hiding in {countdown}s)
                            </div>
                        ) : (
                            <input
                                className="input"
                                readOnly
                                value={apiKey || "No API Key Generated"}
                                style={{ flex: 1, fontFamily: 'monospace', letterSpacing: 1 }}
                            />
                        )}
                        <button
                            className="btn-ghost"
                            onClick={copyToClipboard}
                            style={{ minWidth: 80, color: copied ? 'var(--ok)' : 'inherit' }}
                        >
                            {copied ? "✓" : "COPY"}
                        </button>
                        <button className="btn" onClick={generateApiKey}>
                            {apiKey ? "Regenerate Key" : "Generate Key"}
                        </button>
                    </div>
                    <div style={{ marginTop: 20 }}>
                        <button
                            className="btn-ghost"
                            style={{ border: '1px solid var(--border)', padding: '10px 20px' }}
                            onClick={() => window.open('/api/servers/agent/download', '_blank')}
                        >
                            ⬇ DOWNLOAD AGENT SCRIPT
                        </button>
                    </div>
                </div>

                <div className="card" style={{ marginBottom: 30 }}>
                    <h2 style={{ fontSize: 20, marginBottom: 15, borderBottom: '1px solid #333', paddingBottom: 10 }}>
                        Audit History
                    </h2>
                    {auditLogs.length === 0 ? (
                        <div style={{ color: 'var(--muted)', fontStyle: 'italic' }}>No audit records found.</div>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ textAlign: 'left', color: 'var(--muted)', fontSize: 12 }}>
                                    <th style={{ padding: 10 }}>TIME</th>
                                    <th style={{ padding: 10 }}>USER</th>
                                    <th style={{ padding: 10 }}>ACTION</th>
                                    <th style={{ padding: 10 }}>DETAILS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {auditLogs.map(log => (
                                    <tr key={log.id} style={{ borderBottom: '1px solid #222' }}>
                                        <td style={{ padding: 10, fontSize: 12, color: 'var(--muted)' }}>
                                            {new Date(log.timestamp).toLocaleString()}
                                        </td>
                                        <td style={{ padding: 10, fontWeight: 'bold' }}>
                                            {log.username}
                                        </td>
                                        <td style={{ padding: 10, fontWeight: 'bold', color: 'var(--accent)' }}>
                                            {log.action}
                                        </td>
                                        <td style={{ padding: 10 }}>
                                            {log.details}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                <div className="card">
                    <h2 style={{ fontSize: 20, marginBottom: 15, borderBottom: '1px solid #333', paddingBottom: 10 }}>
                        Asset Inventory (Servers)
                    </h2>
                    {servers.length === 0 ? (
                        <div style={{ color: 'var(--muted)', fontStyle: 'italic' }}>No servers connected yet.</div>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ textAlign: 'left', color: 'var(--muted)', fontSize: 12 }}>
                                    <th style={{ padding: 10 }}>STATUS</th>
                                    <th style={{ padding: 10 }}>NAME</th>
                                    <th style={{ padding: 10 }}>HOSTNAME</th>
                                    <th style={{ padding: 10 }}>IP ADDRESS</th>
                                    <th style={{ padding: 10 }}>OS</th>
                                    <th style={{ padding: 10 }}>LAST SEEN</th>
                                    <th style={{ padding: 10 }}>ACTIONS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {servers.map(server => (
                                    <tr key={server.id} style={{ borderBottom: '1px solid #222' }}>
                                        <td style={{ padding: 10 }}>
                                            <span style={{
                                                color: server.status === 'online' ? 'var(--ok)' : 'var(--danger)',
                                                fontWeight: 'bold'
                                            }}>● {server.status.toUpperCase()}</span>
                                        </td>
                                        <td style={{ padding: 10, fontWeight: 'bold' }}>{server.name}</td>
                                        <td style={{ padding: 10, fontFamily: 'monospace' }}>{server.hostname}</td>
                                        <td style={{ padding: 10, fontFamily: 'monospace' }}>{server.ip_address}</td>
                                        <td style={{ padding: 10 }}>{server.os_info}</td>
                                        <td style={{ padding: 10, fontSize: 12, color: 'var(--muted)' }}>
                                            {new Date(server.last_heartbeat).toLocaleString()}
                                        </td>
                                        <td style={{ padding: 10 }}>
                                            <button
                                                className="btn-ghost"
                                                onClick={() => renameServer(server.id, server.name)}
                                                style={{ marginRight: 5, fontSize: 12 }}
                                            >
                                                RENAME
                                            </button>
                                            {user?.role === 'admin' && (
                                                <>
                                                    <button
                                                        className="btn-ghost"
                                                        onClick={() => setAccessModalServer(server)}
                                                        style={{
                                                            marginRight: 5,
                                                            fontSize: 12,
                                                            color: 'var(--accent)',
                                                            borderColor: 'var(--accent)'
                                                        }}
                                                    >
                                                        ACCESS
                                                    </button>
                                                    <button
                                                        className="btn-ghost btn-danger"
                                                        onClick={() => deleteServer(server.id)}
                                                        style={{ fontSize: 12 }}
                                                    >
                                                        DELETE
                                                    </button>
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {accessModalServer && (
                <ServerAccessModal
                    server={accessModalServer}
                    users={usersList} // Pass all users
                    onClose={() => {
                        setAccessModalServer(null);
                        fetchData(); // Refresh list to get updated assignments if needed
                    }}
                    token={token}
                />
            )}
        </div>
    );
}
