import React, { useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    useEffect(() => {
        logout();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Login form submitted"); // DEBUG
        setError('');
        try {
            console.log("Sending login request...", { email, password }); // DEBUG
            const formData = new FormData();
            formData.append('username', email); // BACKEND EXPECTS 'username' KEY BUT VALUE IS EMAIL
            formData.append('password', password);

            const res = await axios.post('/api/token', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            console.log("Login response:", res.data); // DEBUG

            login(res.data.access_token);
            console.log("Navigating to dashboard..."); // DEBUG
            navigate('/dashboard');
        } catch (err) {
            console.error("Login error full:", err);
            if (err.response) {
                console.error("Response status:", err.response.status);
                console.error("Response data:", JSON.stringify(err.response.data, null, 2));
            }
            setError(err.response?.data?.detail || 'Invalid credentials');
        }
    };

    const [forgotMode, setForgotMode] = useState(false);

    const handleForgot = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await axios.post('/api/forgot-password', { email });
            alert("If that email belongs to an Admin, a password reset link has been sent.");
            setForgotMode(false);
        } catch (err) {
            alert("Request failed.");
        }
    };

    return (
        <div style={{
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column'
        }}>
            <div className="card" style={{ width: 400, padding: 40, textAlign: 'center' }}>
                <h1 className="title" style={{ fontSize: 32, marginBottom: 20 }}>Aegis Access</h1>

                {error && <div style={{ color: 'var(--danger)', marginBottom: 10 }}>{error}</div>}

                <form onSubmit={forgotMode ? handleForgot : handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
                    {!forgotMode && (
                        <input
                            className="input"
                            type="email"
                            placeholder="Email Address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    )}
                    {forgotMode && (
                        <input
                            className="input"
                            type="email"
                            placeholder="Admin Email Address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    )}
                    {!forgotMode && (
                        <input
                            className="input"
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    )}
                    <button className="btn" type="submit">
                        {forgotMode ? "Send Recovery Link" : "Initialize Session"}
                    </button>
                </form>

                <div style={{ marginTop: 15, textAlign: 'center' }}>
                    <button
                        onClick={() => { setForgotMode(!forgotMode); setError(''); }}
                        style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: 13, textDecoration: 'underline' }}
                    >
                        {forgotMode ? "Back to Login" : "Forgot Password?"}
                    </button>
                </div>

                <div style={{ marginTop: 20, fontSize: 14, color: 'var(--muted)' }}>
                    Access Restricted. Contact Administrator for credentials.
                </div>
            </div>
            <div style={{ marginTop: 20, color: 'var(--muted)', fontSize: 12 }}>
                SECURE TERMINAL // AUTHORIZED PERSONNEL ONLY
            </div>
        </div>
    );
}
