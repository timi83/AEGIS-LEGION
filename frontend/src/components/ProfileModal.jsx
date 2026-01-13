
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProfileModal = ({ open, onClose, user, onUpdate }) => {
    if (!open) return null;

    const [username, setUsername] = useState(user?.username || '');
    const [fullName, setFullName] = useState(user?.full_name || '');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (user) {
            setUsername(user.username || '');
            setFullName(user.full_name || '');
        }
    }, [user]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const res = await axios.put('/api/me/profile', {
                username,
                full_name: fullName
            });
            onUpdate(res.data); // Notify parent of new user data
            onClose();
        } catch (err) {
            console.error(err);
            setError('Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal">
                <div className="modal-header">
                    <h2>Identity Configuration</h2>
                    <button className="btn-icon" onClick={onClose}>&times;</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="modal-body">
                        {error && <div className="error-message" style={{ color: 'var(--danger)', marginBottom: 10 }}>{error}</div>}

                        <div className="form-group">
                            <label>Designation (Username)</label>
                            <input
                                className="input"
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                            />
                            <small style={{ color: 'var(--muted)' }}>This is your public display name.</small>
                        </div>

                        <div className="form-group">
                            <label>Full Personnel Name</label>
                            <input
                                className="input"
                                value={fullName}
                                onChange={e => setFullName(e.target.value)}
                            />
                        </div>

                        <div className="form-group">
                            <label>Email (Immutable)</label>
                            <input className="input" value={user?.email || ''} disabled style={{ opacity: 0.5 }} />
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn" disabled={loading}>
                            {loading ? 'Updating...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ProfileModal;
