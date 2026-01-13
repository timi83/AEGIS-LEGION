import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div style={{
            minHeight: '100vh',
            background: 'var(--bg-dark)',
            color: 'var(--text-main)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            position: 'relative'
        }}>
            {/* Global styles and animations */}
            <style>{`
                @keyframes fadeInUp {
                    0% {
                        opacity: 0;
                        transform: translateY(40px);
                    }
                    100% {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @keyframes glowPulse {
                    0%, 100% {
                        text-shadow: 0 0 20px rgba(0, 255, 157, 0.5);
                    }
                    50% {
                        text-shadow: 0 0 35px rgba(0, 255, 157, 0.8);
                    }
                }

                @keyframes moveGrid {
                    0% {
                        background-position: 0px 0px, 0px 0px;
                    }
                    100% {
                        background-position: 50px 50px, 50px 50px;
                    }
                }

                @keyframes scanLine {
                    0% {
                        transform: translateY(-100vh);
                    }
                    100% {
                        transform: translateY(200vh);
                    }
                }

                .btn, .btn-ghost {
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .btn:hover, .btn-ghost:hover {
                    transform: scale(1.05);
                    box-shadow: 0 0 40px rgba(0, 255, 157, 0.4);
                }

                .feature-card {
                    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .feature-card:hover {
                    transform: translateY(-15px);
                    border-color: var(--accent);
                    box-shadow: 0 20px 40px rgba(0, 255, 157, 0.25);
                }

                .scan-container {
                    position: absolute;
                    inset: 0;
                    pointer-events: none;
                    z-index: 1;
                    overflow: hidden;
                }

                .scan-line {
                    position: absolute;
                    left: 0;
                    width: 100%;
                    height: 2px;
                    background: var(--accent);
                    opacity: 0.25;
                    box-shadow: 0 0 30px var(--accent), 0 0 60px rgba(0, 255, 157, 0.3);
                    animation: scanLine 20s linear infinite;
                }

                .scan-line:nth-child(2) {
                    animation-delay: 10s;
                }
            `}</style>

            {/* Subtle scanning effect overlay */}
            <div className="scan-container">
                <div className="scan-line"></div>
                <div className="scan-line"></div>
            </div>

            {/* Nav */}
            <nav style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: 'clamp(1.5rem, 4vw, 2rem) clamp(2rem, 6vw, 3.5rem)',
                alignItems: 'center',
                zIndex: 10,
                flexWrap: 'wrap',
                gap: '1rem'
            }}>
                <div style={{ 
                    fontSize: 'clamp(1.6rem, 4.5vw, 2rem)', 
                    fontWeight: 'bold', 
                    letterSpacing: '3px', 
                    color: 'var(--accent)',
                    textShadow: '0 0 20px rgba(0, 255, 157, 0.5)',
                    animation: 'glowPulse 4s ease-in-out infinite'
                }}>
                    AEGIS LEGION
                </div>
                <div style={{ display: 'flex', gap: 'clamp(10px, 2vw, 15px)' }}>
                    <button onClick={() => navigate('/login')} className="btn-ghost">LOGIN</button>
                    <button onClick={() => navigate('/register')} className="btn">ACCESS TERMINAL</button>
                </div>
            </nav>

            {/* Hero Section */}
            <main style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                textAlign: 'center',
                padding: '0 clamp(1.25rem, 5vw, 2.5rem)',
                zIndex: 10,
                background: 'radial-gradient(circle at center, rgba(0, 255, 157, 0.08) 0%, transparent 70%)'
            }}>
                <h1 style={{
                    fontSize: 'clamp(3rem, 8vw, 4.2rem)',
                    textTransform: 'uppercase',
                    marginBottom: '20px',
                    fontWeight: 800,
                    textShadow: '0 0 30px rgba(0, 255, 157, 0.6)',
                    animation: 'fadeInUp 1.2s cubic-bezier(0.4, 0, 0.2, 1) both, glowPulse 5s ease-in-out infinite'
                }}>
                    Global Command <span style={{ color: 'var(--accent)' }}>Center</span>
                </h1>
                <p style={{
                    fontSize: 'clamp(1rem, 2.5vw, 1.3rem)',
                    maxWidth: 'clamp(500px, 70vw, 800px)',
                    lineHeight: '1.7',
                    color: 'var(--text-muted)',
                    marginBottom: '50px',
                    animation: 'fadeInUp 1.2s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both'
                }}>
                    Centralized threat detection and infrastructure monitoring for the modern enterprise.
                    Secure your assets with military-grade surveillance and automated response protocols.
                </p>
                <div style={{ 
                    display: 'flex', 
                    gap: 'clamp(20px, 4vw, 25px)',
                    flexWrap: 'wrap',
                    justifyContent: 'center',
                    animation: 'fadeInUp 1.2s cubic-bezier(0.4, 0, 0.2, 1) 0.6s both'
                }}>
                    <button
                        onClick={() => navigate('/register')}
                        className="btn"
                        style={{ 
                            padding: 'clamp(12px, 2vw, 16px) clamp(35px, 6vw, 45px)', 
                            fontSize: 'clamp(1.1rem, 2.2vw, 1.3rem)',
                            boxShadow: '0 0 35px rgba(0, 255, 157, 0.25)' 
                        }}
                    >
                        GET STARTED
                    </button>
                    <button
                        onClick={() => navigate('/login')}
                        className="btn-ghost"
                        style={{ 
                            padding: 'clamp(12px, 2vw, 16px) clamp(35px, 6vw, 45px)', 
                            fontSize: 'clamp(1.1rem, 2.2vw, 1.3rem)'
                        }}
                    >
                        LIVE DEMO
                    </button>
                </div>
            </main>

            {/* Features */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                gap: 'clamp(30px, 6vw, 50px)',
                padding: 'clamp(50px, 10vw, 80px) clamp(2rem, 6vw, 3.5rem)',
                background: 'rgba(0,0,0,0.4)',
                zIndex: 10
            }}>
                <FeatureCard 
                    title="REAL-TIME MONITORING" 
                    desc="Live heartbeat tracking of all organization assets." 
                    delay="1.2s" 
                />
                <FeatureCard 
                    title="THREAT DETECTION" 
                    desc="Automated anomaly detection using advanced heuristics." 
                    delay="1.4s" 
                />
                <FeatureCard 
                    title="DATA ISOLATION" 
                    desc="Strict multi-tenant architecture ensures data sovereignty." 
                    delay="1.6s" 
                />
            </div>

            {/* Animated background grid */}
            <div style={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                backgroundImage: 'linear-gradient(var(--border) 1px, transparent 1px), linear-gradient(90deg, var(--border) 1px, transparent 1px)',
                backgroundSize: '50px 50px',
                opacity: 0.15,
                pointerEvents: 'none',
                transform: 'perspective(600px) rotateX(60deg) translateY(-50px) scale(1.8)',
                animation: 'moveGrid 60s linear infinite',
                zIndex: 0
            }} />
        </div>
    );
}

function FeatureCard({ title, desc, delay }) {
    return (
        <div 
            className="feature-card"
            style={{
                border: '1px solid var(--border)',
                padding: 'clamp(30px, 6vw, 40px)',
                background: 'var(--card-bg)',
                borderRadius: '16px',
                backdropFilter: 'blur(4px)',
                animation: `fadeInUp 1.2s cubic-bezier(0.4, 0, 0.2, 1) ${delay} both`
            }}
        >
            <div style={{
                height: '5px',
                width: 'clamp(50px, 10vw, 70px)',
                background: 'var(--accent)',
                borderRadius: '3px',
                marginBottom: '30px',
                boxShadow: '0 0 20px rgba(0, 255, 157, 0.6)'
            }} />
            <h3 style={{ 
                color: 'var(--accent)', 
                marginBottom: '15px', 
                fontSize: 'clamp(1.4rem, 3.5vw, 1.8rem)',
                letterSpacing: '1px'
            }}>
                {title}
            </h3>
            <p style={{ 
                color: 'var(--text-muted)', 
                fontSize: 'clamp(0.95rem, 2vw, 1.1rem)', 
                lineHeight: '1.6' 
            }}>
                {desc}
            </p>
        </div>
    );
}