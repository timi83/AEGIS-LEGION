import React, { useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { EventsContext } from '../context/EventsContext';
import ProfileModal from './ProfileModal';

export default function Navbar() {
    const { user, logout, refreshUser, token } = useContext(AuthContext);
    const { lastEvent } = useContext(EventsContext);
    const navigate = useNavigate();
    const location = useLocation();
    const [isProfileOpen, setIsProfileOpen] = React.useState(false);

    // Notifications State
    const [notifs, setNotifs] = useState([]);
    const [showNotifs, setShowNotifs] = useState(false);
    const unreadCount = notifs.filter(n => !n.is_read).length;

    useEffect(() => {
        if (!token) return;
        fetchNotifications();

        // Poll backup
        const interval = setInterval(fetchNotifications, 60000); // Very relaxed polling

        return () => {
            clearInterval(interval);
        };
    }, [token]);

    // React to Global Events
    useEffect(() => {
        if (!lastEvent) return;
        if (lastEvent.type === "assignment_update" ||
            lastEvent.type === "note_added" ||
            lastEvent.type === "incident_created") {
            fetchNotifications();
        }
    }, [lastEvent]);

    async function fetchNotifications() {
        try {
            const res = await axios.get('/api/notifications/', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setNotifs(res.data);
        } catch (e) {
            console.error("Failed to fetch notifications", e);
        }
    }

    async function handleNotifClick(n) {
        // Mark read
        try {
            await axios.put(`/api/notifications/${n.id}/read`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setNotifs(prev => prev.map(x => x.id === n.id ? { ...x, is_read: true } : x));
            setShowNotifs(false);
            if (n.link) navigate(n.link);
        } catch (e) { console.error(e); }
    }

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const getRoleDisplay = (role) => {
        const mapping = {
            'admin': 'ADMINISTRATOR',
            'analyst': 'ANALYST',
            'viewer': 'VIEWER'
        };
        return mapping[role] || (role ? role.toUpperCase() : 'OPERATIVE');
    };

    return (
        <nav className="navbar">
            <div className="nav-brand">
                <div className="nav-logo">AEGIS LEGION</div>
                <div className="nav-status">
                    <div className="status-dot"></div>
                    SYSTEM ONLINE
                </div>
            </div>

            <div className="nav-user" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>

                {/* NOTIFICATIONS BELL */}
                <div style={{ position: 'relative' }}>
                    <button
                        className="btn-ghost"
                        style={{ position: 'relative', fontSize: '18px', padding: '8px' }}
                        onClick={() => setShowNotifs(!showNotifs)}
                    >
                        🔔
                        {unreadCount > 0 && (
                            <span style={{
                                position: 'absolute',
                                top: '0px',
                                right: '0px',
                                background: 'var(--danger)',
                                color: '#fff',
                                fontSize: '10px',
                                borderRadius: '50%',
                                width: '16px',
                                height: '16px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontWeight: 'bold'
                            }}>
                                {unreadCount}
                            </span>
                        )}
                    </button>

                    {showNotifs && (
                        <div className="card animate-fade-in" style={{
                            position: 'absolute',
                            top: '40px',
                            right: '0',
                            width: '300px',
                            maxHeight: '400px',
                            overflowY: 'auto',
                            zIndex: 1000,
                            border: '1px solid var(--accent)',
                            background: 'rgba(0,0,0,0.95)',
                            padding: '0'
                        }}>
                            <div style={{ padding: '8px 12px', borderBottom: '1px solid #333', fontSize: '12px', color: 'var(--text-muted)' }}>
                                NOTIFICATIONS
                            </div>
                            {notifs.length === 0 ? (
                                <div style={{ padding: '16px', textAlign: 'center', fontSize: '12px', color: '#666' }}>
                                    No notifications.
                                </div>
                            ) : (
                                notifs.map(n => (
                                    <div
                                        key={n.id}
                                        onClick={() => handleNotifClick(n)}
                                        style={{
                                            padding: '12px',
                                            borderBottom: '1px solid #222',
                                            background: n.is_read ? 'transparent' : 'rgba(0, 255, 157, 0.05)',
                                            cursor: 'pointer',
                                            transition: 'background 0.2s'
                                        }}
                                        onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                                        onMouseLeave={e => e.currentTarget.style.background = n.is_read ? 'transparent' : 'rgba(0, 255, 157, 0.05)'}
                                    >
                                        <div style={{ fontSize: '13px', fontWeight: n.is_read ? 'normal' : 'bold', color: 'var(--text-main)' }}>
                                            {n.title}
                                        </div>
                                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                                            {n.message}
                                        </div>
                                        <div style={{ fontSize: '10px', color: '#555', marginTop: '4px', textAlign: 'right' }}>
                                            {new Date(n.timestamp).toLocaleTimeString()}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>

                <div className="user-info" onClick={() => setIsProfileOpen(true)} style={{ cursor: 'pointer' }}>
                    <div className="user-name">{user?.username || user?.sub || 'Commander'}</div>
                    <div className="user-role">{getRoleDisplay(user?.role)}</div>
                </div>
                {location.pathname === '/dashboard' && (
                    <button className="btn-ghost" onClick={() => navigate('/rules')} style={{ marginRight: 8 }}>RULES</button>
                )}
                {/* ... existing logic ... */}
                {/* Redundant location checks logic kept for compatibility */}
                {location.pathname === '/rules' && (
                    <button className="btn-ghost" onClick={() => navigate('/dashboard')} style={{ marginRight: 8 }}>DASHBOARD</button>
                )}
                {location.pathname !== '/settings' && location.pathname !== '/dashboard' && location.pathname !== '/rules' && (
                    <button className="btn-ghost" onClick={() => navigate('/dashboard')} style={{ marginRight: 8 }}>HOME</button>
                )}
                {location.pathname !== '/settings' && (
                    <button className="btn-ghost" onClick={() => navigate('/settings')} style={{ marginRight: 8 }}>SETTINGS</button>
                )}
                {location.pathname === '/settings' && (
                    <button className="btn-ghost" onClick={() => navigate('/dashboard')} style={{ marginRight: 8 }}>DASHBOARD</button>
                )}
                <button className="btn-ghost btn-danger" onClick={handleLogout}>
                    LOGOUT
                </button>
            </div>

            <ProfileModal
                open={isProfileOpen}
                onClose={() => setIsProfileOpen(false)}
                user={user}
                onUpdate={(updatedUser) => {
                    refreshUser();
                }}
            />
        </nav >
    );
}
