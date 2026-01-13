import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function ResetPassword() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');

    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [status, setStatus] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirm) {
            setStatus("Passwords do not match");
            return;
        }

        try {
            setStatus("Updating password...");
            await axios.post('/api/reset-password', {
                token: token,
                new_password: password
            });
            setStatus("Password updated! Redirecting to login...");
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            console.error(err);
            setStatus("Failed to reset password: " + (err.response?.data?.detail || err.message));
        }
    };

    if (!token) {
        return <div style={{ padding: 40, color: '#fff', textAlign: 'center' }}>Invalid or missing token.</div>;
    }

    return (
        <div style={{
            height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column'
        }}>
            <div className="card" style={{ width: 400, padding: 40, textAlign: 'center' }}>
                <h1 className="title" style={{ fontSize: 24, marginBottom: 20 }}>Reset Password</h1>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
                    <input
                        className="input"
                        type="password"
                        placeholder="New Password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        required
                        minLength={6}
                    />
                    <input
                        className="input"
                        type="password"
                        placeholder="Confirm Password"
                        value={confirm}
                        onChange={e => setConfirm(e.target.value)}
                        required
                    />
                    <button className="btn" type="submit">Set New Password</button>
                </form>

                {status && <div style={{ marginTop: 20, color: status.includes("updated") ? 'var(--ok)' : 'var(--danger)' }}>{status}</div>}
            </div>
        </div>
    );
}
