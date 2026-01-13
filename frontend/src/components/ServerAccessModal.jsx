
import React, { useState } from 'react';
import axios from 'axios';

export default function ServerAccessModal({ server, users, onClose, token, apiBase = "/api" }) {
    const [allowedIds, setAllowedIds] = useState(server.allowed_user_ids || []);
    const [loadingMap, setLoadingMap] = useState({}); // Track loading state per user

    const toggleAccess = async (user) => {
        const isAssigned = allowedIds.includes(user.id);
        const action = isAssigned ? 'revoke' : 'grant';

        // Optimistic UI Update
        setAllowedIds(prev => isAssigned ? prev.filter(id => id !== user.id) : [...prev, user.id]);
        setLoadingMap(prev => ({ ...prev, [user.id]: true }));

        try {
            if (isAssigned) {
                // DELETE /servers/:id/assign/:uid
                await axios.delete(`${apiBase}/servers/${server.id}/assign/${user.id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            } else {
                // POST /servers/:id/assign {user_id}
                await axios.post(`${apiBase}/servers/${server.id}/assign`,
                    { user_id: user.id },
                    { headers: { Authorization: `Bearer ${token}` } }
                );
            }
        } catch (err) {
            console.error(err);
            alert(`Failed to ${action} access for ${user.username}`);
            // Revert on error
            setAllowedIds(prev => isAssigned ? [...prev, user.id] : prev.filter(id => id !== user.id));
        } finally {
            setLoadingMap(prev => ({ ...prev, [user.id]: false }));
        }
    };

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999
        }} onClick={onClose}>
            <div className="card" style={{ width: 400, maxHeight: '80vh', overflowY: 'auto' }} onClick={e => e.stopPropagation()}>
                <h2 style={{ borderBottom: '1px solid #333', paddingBottom: 10, marginBottom: 15 }}>
                    Manage Access: {server.hostname}
                </h2>
                <p style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 20 }}>
                    Select users who can view this server. <br />
                    <em style={{ fontSize: 11 }}>Admins and the Owner ({server.name || 'Server'}) always have access.</em>
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {users.map(u => {
                        // Skip if user is admin (implicit access) or owner? 
                        // Backend logic: Admin sees everything. Owner sees own.
                        // So assigning Admin is redundant but harmless.
                        // Assigning Owner is redundant.
                        // Let's show visual indicator for implicit access.
                        const isOwner = false; // We don't have owner ID here easily unless passed. server.user_id? 
                        // Assuming list_servers didn't return user_id... checking model... yes it does? Schema omitted it.
                        // Let's just list everyone.

                        const isAssigned = allowedIds.includes(u.id);
                        const isLoading = loadingMap[u.id];

                        let badge = null;
                        if (u.role === 'admin') badge = <span className="badge ok">ADMIN (ALL)</span>;

                        // Disable interaction for admins as they have global access
                        const disabled = u.role === 'admin' || isLoading;

                        return (
                            <div key={u.id} style={{
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                padding: '8px', border: '1px solid #333', borderRadius: 4,
                                background: isAssigned ? 'rgba(0, 255, 157, 0.05)' : 'transparent'
                            }}>
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span style={{ fontWeight: 600 }}>{u.username}</span>
                                    <span style={{ fontSize: 11, color: 'var(--muted)' }}>{u.role}</span>
                                </div>

                                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                    {badge}
                                    {!badge && (
                                        <label className="switch">
                                            <input
                                                type="checkbox"
                                                checked={isAssigned}
                                                disabled={disabled}
                                                onChange={() => toggleAccess(u)}
                                            />
                                            <span className="slider round"></span>
                                        </label>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div style={{ marginTop: 20, textAlign: 'right' }}>
                    <button className="btn" onClick={onClose}>Done</button>
                </div>
            </div>
        </div>
    );
}
