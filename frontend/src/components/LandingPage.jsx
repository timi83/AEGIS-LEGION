import React from 'react';
import { useNavigate } from 'react-router-dom';
import DottedSurface from './DottedSurface';

const features = [
    {
        title: 'REAL-TIME MONITORING',
        desc: 'Live heartbeat tracking of all organization assets.',
    },
    {
        title: 'THREAT DETECTION',
        desc: 'Automated anomaly detection using advanced heuristics.',
    },
    {
        title: 'DATA ISOLATION',
        desc: 'Strict multi-tenant architecture ensures data sovereignty.',
    },
];

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div style={{
            position: 'relative',
            minHeight: '100vh',
            overflow: 'hidden',

            // backgroundColor: 'black', // Removed to reveal dots
            color: 'white',
        }}>
            {/* 3D Background */}
            <DottedSurface />

            {/* Global Animations & Styles */}
            <style>{`
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(40px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes glowPulse {
                    0%, 100% { 
                        text-shadow: 0 0 20px rgba(0, 255, 157, 0.5); 
                    }
                    50% { 
                        text-shadow: 0 0 35px rgba(0, 255, 157, 0.8); 
                    }
                }
                @keyframes scanLine {
                    0% { transform: translateY(-100vh); }
                    100% { transform: translateY(200vh); }
                }
                @keyframes float {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-12px); }
                }

                .animate-fadeInUp {
                    animation: fadeInUp 1.2s cubic-bezier(0.4, 0, 0.2, 1) both;
                }
                .animate-glowPulse {
                    animation: glowPulse 6s ease-in-out infinite;
                }
                .animate-float {
                    animation: float 6s ease-in-out infinite;
                }
                
                .hover-scale {
                    transition: transform 0.3s ease, background-color 0.3s, box-shadow 0.3s;
                }
                .hover-scale:hover {
                    transform: scale(1.05);
                }
                
                .scan-line {
                    position: absolute;
                    left: 0;
                    width: 100%;
                    height: 1px;
                    background: #00ff9d;
                    opacity: 0.3;
                    box-shadow: 0 0 30px #00ff9d;
                    animation: scanLine 20s linear infinite;
                    pointer-events: none;
                    z-index: 20;
                }
            `}</style>

            {/* Background Overlays */}
            <div style={{
                pointerEvents: 'none',
                position: 'fixed',
                inset: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.25)', // Very transparent black to aid legibility
                backdropFilter: 'blur(1px)', // Slight blur to help text pop
                zIndex: 0
            }} />

            {/* Scan Lines */}
            <div className="scan-line" />
            <div className="scan-line" style={{ animationDelay: '10s', boxShadow: '0 0 60px rgba(0,255,157,0.3)' }} />

            {/* Content Container */}
            <div style={{ position: 'relative', zIndex: 30, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>

                {/* Navbar */}
                <nav style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '2.5rem 2rem', /* px-8 py-10 */
                    maxWidth: '1280px',
                    margin: '0 auto',
                    width: '100%'
                }}>
                    <div className="animate-glowPulse" style={{
                        fontSize: 'clamp(1.2rem, 3vw, 2rem)',
                        fontWeight: 900,
                        letterSpacing: '0.05em',
                        color: '#00ff9d',
                        textShadow: '0 0 20px rgba(0,255,157,0.5)'
                    }}>
                        AEGIS LEGION
                    </div>

                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button
                            onClick={() => navigate('/login')}
                            className="hover-scale"
                            style={{
                                background: 'transparent',
                                border: '1px solid #00ff9d',
                                color: '#00ff9d',
                                padding: '0.75rem 1.5rem',
                                borderRadius: '0.5rem',
                                fontWeight: 500,
                                fontSize: '1rem',
                                cursor: 'pointer',
                            }}
                        >
                            LOGIN
                        </button>
                        <button
                            onClick={() => navigate('/register')}
                            className="hover-scale"
                            style={{
                                background: '#00ff9d',
                                border: 'none',
                                color: 'black',
                                padding: '0.75rem 1.5rem',
                                borderRadius: '0.5rem',
                                fontWeight: 700,
                                fontSize: '1rem',
                                cursor: 'pointer',
                                boxShadow: '0 0 35px rgba(0,255,157,0.25)'
                            }}
                        >
                            ACCESS TERMINAL
                        </button>
                    </div>
                </nav>

                {/* Hero Section */}
                <main style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center',
                    padding: '0 2rem'
                }}>
                    <h1 className="animate-fadeInUp animate-glowPulse" style={{
                        marginBottom: '1.5rem',
                        fontSize: 'clamp(2rem, 6vw, 4.5rem)',
                        textTransform: 'uppercase',
                        fontWeight: 900,
                        lineHeight: 1.1,
                        textShadow: '0 0 30px rgba(0,255,157,0.6)'
                    }}>
                        Global Command <span style={{ color: '#00ff9d' }}>Center</span>
                    </h1>

                    <p className="animate-fadeInUp" style={{
                        marginBottom: '2.5rem',
                        maxWidth: '48rem',
                        fontSize: 'clamp(1rem, 1.5vw, 1.25rem)',
                        color: '#9ca3af', /* text-gray-400 */
                        animationDelay: '0.3s',
                        lineHeight: 1.6
                    }}>
                        Centralized threat detection and infrastructure monitoring for the modern enterprise.
                        Secure your assets with military-grade surveillance and automated response protocols.
                    </p>

                    <div className="animate-fadeInUp" style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        justifyContent: 'center',
                        gap: '2rem',
                        animationDelay: '0.6s'
                    }}>
                        <button
                            onClick={() => navigate('/register')}
                            className="hover-scale"
                            style={{
                                background: '#00ff9d',
                                color: 'black',
                                padding: '1.25rem 3rem',
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                borderRadius: '0.5rem',
                                border: 'none',
                                cursor: 'pointer',
                                boxShadow: '0 0 40px rgba(0,255,157,0.4)'
                            }}
                        >
                            GET STARTED
                        </button>
                        <button
                            onClick={() => navigate('/login')}
                            className="hover-scale"
                            style={{
                                background: 'transparent',
                                border: '2px solid #00ff9d',
                                color: '#00ff9d',
                                padding: '1.25rem 3rem',
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                borderRadius: '0.5rem',
                                cursor: 'pointer'
                            }}
                        >
                            LIVE DEMO
                        </button>
                    </div>
                </main>

                {/* Features Section */}
                <section className="animate-fadeInUp" style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '3rem',
                    padding: '5rem 2rem', /* py-20 px-8 */
                    maxWidth: '1280px',
                    margin: '0 auto',
                    width: '100%',
                    // background: 'rgba(0,0,0,0.4)', // Removed per user request
                    animationDelay: '0.9s'
                }}>
                    {features.map((feature, i) => (
                        <FeatureCard key={i} title={feature.title} desc={feature.desc} delay={1.2 + i * 0.2} floatDelay={i * 1.5} />
                    ))}
                </section>
            </div>
        </div>
    );
}

function FeatureCard({ title, desc, delay, floatDelay }) {
    const [hover, setHover] = React.useState(false);

    return (
        <div
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
            className="animate-fadeInUp"
            style={{
                borderRadius: '0.75rem',
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: hover ? '#00ff9d' : 'rgba(0, 255, 157, 0.2)',
                background: hover ? 'linear-gradient(180deg, rgba(0,255,157,0.05) 0%, rgba(0,0,0,0.6) 100%)' : 'rgba(0,0,0,0.5)',
                backdropFilter: 'blur(4px)',
                padding: '2.5rem',
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                transform: hover ? 'translateY(-1.5rem)' : 'none',
                boxShadow: hover ? '0 20px 40px rgba(0,255,157,0.25)' : 'none',
                animation: `fadeInUp 1.2s cubic-bezier(0.4, 0, 0.2, 1) ${delay}s both, float 6s ease-in-out infinite ${floatDelay}s`,
                // Note: animationDelay logic is moved into the animation shorthand above to handle multiple animations
            }}
        >
            <div style={{
                marginBottom: '2rem',
                height: '0.25rem',
                width: '5rem',
                borderRadius: '0.125rem',
                backgroundColor: '#00ff9d',
                boxShadow: '0 0 20px rgba(0,255,157,0.6)'
            }} />
            <h3 className="animate-glowPulse" style={{
                marginBottom: '1rem',
                fontSize: '1.5rem', /* 2xl */
                letterSpacing: '0.05em',
                color: '#00ff9d',
                fontWeight: 600
            }}>
                {title}
            </h3>
            <p style={{
                fontSize: '1.125rem', /* lg */
                color: '#9ca3af',
                lineHeight: 1.6
            }}>
                {desc}
            </p>
        </div>
    );
}