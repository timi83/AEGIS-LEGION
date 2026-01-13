import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

export default function Register() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [fullName, setFullName] = useState('');
    const [organization, setOrganization] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();
    const { logout } = useContext(AuthContext);

    useEffect(() => {
        logout();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Register form submitted"); // DEBUG
        setError('');
        setSuccess('');
        try {
            console.log("Sending register request...", { username, email }); // DEBUG
            await axios.post('/api/register', {
                username,
                password,
                email,
                full_name: fullName,
                organization
            });
            console.log("Registration successful"); // DEBUG
            setSuccess('Registration successful! Redirecting to login...');
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            console.error("Registration error full object:", err);
            if (err.response) {
                console.error("Response data:", JSON.stringify(err.response.data, null, 2));
                console.error("Response status:", err.response.status);
            }
            // Handle array of details (validation errors) or string
            const detail = err.response?.data?.detail;
            const message = Array.isArray(detail) ? JSON.stringify(detail) : (detail || 'Registration failed');
            setError(message);
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
                <h1 className="title" style={{ fontSize: 32, marginBottom: 20 }}>New Operative</h1>

                {error && <div style={{ color: 'var(--danger)', marginBottom: 10 }}>{error}</div>}
                {success && <div style={{ color: 'var(--ok)', marginBottom: 10 }}>{success}</div>}

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
                    <input
                        className="input"
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <input
                        className="input"
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <input
                        className="input"
                        type="text"
                        placeholder="Full Name"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        required
                    />
                    <input
                        className="input"
                        type="text"
                        placeholder="Organization"
                        value={organization}
                        onChange={(e) => setOrganization(e.target.value)}
                        required
                    />
                    <input
                        className="input"
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button className="btn" type="submit">Register</button>
                </form>

                <div style={{ marginTop: 20, fontSize: 14 }}>
                    Already have an account? <Link to="/login" style={{ color: 'var(--muted)' }}>Login</Link>
                </div>
            </div>
            <div style={{ marginTop: 20, color: 'var(--muted)', fontSize: 12 }}>
                SECURE TERMINAL // AUTHORIZED PERSONNEL ONLY
            </div>
        </div>
    );
}
