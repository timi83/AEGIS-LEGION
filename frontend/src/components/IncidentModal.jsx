import React, { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";
import { EventsContext } from "../context/EventsContext";

export default function IncidentModal({ incident, onClose, apiBase = "/api" }) {
    const { token, user } = useContext(AuthContext);
    const [note, setNote] = useState("");
    const [notes, setNotes] = useState([]);
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef(null);

    const [mentionableUsers, setMentionableUsers] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [suggestionQuery, setSuggestionQuery] = useState("");
    const [cursorPos, setCursorPos] = useState(0);

    const { lastEvent } = useContext(EventsContext); // Added useContext for EventsContext

    // Fetch notes on open
    useEffect(() => {
        if (!incident?.id) return;
        fetchNotes();
        fetchMentionableUsers();

        const intv = setInterval(fetchNotes, 10000); // Relaxed polling fallback
        return () => clearInterval(intv);
    }, [incident.id]);

    // React to Global Events
    useEffect(() => {
        if (!lastEvent) return;
        if (lastEvent.type === "note_added" && String(lastEvent.incident_id) === String(incident.id)) {
            fetchNotes();
        }
    }, [lastEvent]);

    async function fetchMentionableUsers() {
        try {
            const res = await axios.get(`${apiBase}/users/mentionable`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            // Add @everyone option
            const everyone = { username: "everyone", role: "broadcast" };
            setMentionableUsers([everyone, ...res.data]);
        } catch (e) {
            console.error("Failed to fetch mentionable users", e);
        }
    }

    async function fetchNotes() {
        try {
            const res = await axios.get(`${apiBase}/incidents/${incident.id}/notes`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setNotes(res.data);
            scrollToBottom();
        } catch (e) {
            console.error("Failed to fetch notes", e);
        }
    }

    function scrollToBottom() {
        if (scrollRef.current) {
            setTimeout(() => {
                scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
            }, 100);
        }
    }

    async function submitNote() {
        if (!note.trim()) return;
        setLoading(true);
        try {
            const res = await axios.post(
                `${apiBase}/incidents/${incident.id}/notes`,
                { content: note },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setNote("");
            fetchNotes(); // Refresh immediately
        } catch (e) {
            console.error("Failed to add note", e);
            alert("Failed to add note: " + (e.response?.data?.detail || e.message));
        } finally {
            setLoading(false);
        }
    }

    // Autocomplete Logic
    const handleInputChange = (e) => {
        const val = e.target.value;
        setNote(val);
        setCursorPos(e.target.selectionStart);

        // Check for @ match at cursor
        const lastAt = val.lastIndexOf('@', e.target.selectionStart);
        if (lastAt !== -1) {
            const query = val.substring(lastAt + 1, e.target.selectionStart);
            // Only show if no spaces (single word typing)
            if (!query.includes(' ')) {
                setSuggestionQuery(query);
                setShowSuggestions(true);
                return;
            }
        }
        setShowSuggestions(false);
    };

    const insertMention = (username) => {
        const lastAt = note.lastIndexOf('@', cursorPos);
        if (lastAt !== -1) {
            const prefix = note.substring(0, lastAt);
            const suffix = note.substring(cursorPos);
            const newText = `${prefix}@${username} ${suffix}`;
            setNote(newText);
            setShowSuggestions(false);
        }
    };

    const formatMessage = (content, isMe) => {
        // High-contrast highlighting logic
        const tokens = content.split(" ");
        return tokens.map((token, i) => {
            if (token === "@everyone") {
                return (
                    <span key={i} style={{
                        color: isMe ? '#000' : '#FFD700',
                        fontWeight: '900',
                        textShadow: isMe ? 'none' : '0 0 10px rgba(255, 215, 0, 0.4)',
                        background: isMe ? 'rgba(255,255,255,0.2)' : 'rgba(255, 215, 0, 0.1)',
                        padding: '0 4px',
                        borderRadius: '4px'
                    }}>{token} </span>
                );
            }
            if (token.startsWith("@")) {
                // If it's ME (Accent bubble), use Black/White contrast.
                // If it's OTHERS (Dark bubble), use Accent contrast.
                return (
                    <span key={i} style={{
                        color: isMe ? '#000' : 'var(--accent)',
                        fontWeight: 'bold',
                        background: isMe ? 'rgba(255,255,255,0.3)' : 'rgba(0, 255, 255, 0.1)',
                        padding: '0 2px',
                        borderRadius: '2px'
                    }}>{token} </span>
                );
            }
            return token + " ";
        });
    };

    return (
        <div className="fixed inset-0 flex items-center justify-center z-50" style={{ background: 'rgba(0, 0, 0, 0.85)', backdropFilter: 'blur(8px)' }}>
            <div className="card animate-fade-in" style={{ width: '100%', maxWidth: '700px', height: '80vh', display: 'flex', flexDirection: 'column', margin: '24px', border: '1px solid var(--panel-border)', boxShadow: '0 20px 50px rgba(0,0,0,0.5)' }}>

                {/* Header */}
                <div className="flex justify-between items-center mb-0" style={{ borderBottom: '1px solid var(--panel-border)', padding: '16px', background: 'rgba(255,255,255,0.02)' }}>
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', fontSize: '12px', opacity: 0.7 }}>INCIDENT #{incident.id}</span>
                            <span className={`badge ${incident.severity}`}>{incident.severity}</span>
                        </div>
                        <h2 className="text-xl font-bold" style={{ color: '#fff', letterSpacing: '0.5px' }}>{incident.title}</h2>
                    </div>
                    <button onClick={onClose} className="btn-ghost" style={{ padding: '8px', fontSize: '18px', opacity: 0.7 }}>✕</button>
                </div>

                {/* Description */}
                <div style={{ fontSize: '13px', color: '#aaa', padding: '12px 16px', background: '#0a0a0a', borderBottom: '1px solid var(--panel-border)' }}>
                    {incident.description}
                </div>

                {/* Chat Area */}
                <div
                    ref={scrollRef}
                    style={{
                        flex: 1,
                        background: '#111',
                        padding: '20px',
                        overflowY: 'auto',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '16px'
                    }}
                >
                    {notes.length === 0 ? (
                        <div style={{ textAlign: 'center', color: '#444', marginTop: '40px', fontSize: '14px', fontStyle: 'italic' }}>
                            Start the investigation by adding a note...
                        </div>
                    ) : (
                        notes.map((msg) => {
                            // Check ID match first (robust), then username (fallback)
                            const isMe = (msg.user_id && user?.id && msg.user_id === user.id) || (msg.user === user?.username);
                            const isSystem = msg.is_system;

                            if (isSystem) {
                                return (
                                    <div key={msg.id} style={{ display: 'flex', justifyContent: 'center', margin: '8px 0' }}>
                                        <div style={{
                                            background: 'rgba(255, 255, 255, 0.05)',
                                            padding: '4px 12px',
                                            borderRadius: '100px',
                                            fontSize: '11px',
                                            color: '#888',
                                            border: '1px solid rgba(255,255,255,0.05)'
                                        }}>
                                            <span style={{ fontWeight: '600', color: '#aaa' }}>SYSTEM:</span> {msg.content} <span style={{ opacity: 0.5 }}>{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        </div>
                                    </div>
                                );
                            }

                            // Role styling with higher contrast
                            let bubbleColor = '#222';
                            let textColor = '#eee';
                            let borderColor = '#333';
                            let align = 'flex-start'; // Default LEFT (Received)
                            let metaAlign = 'flex-start';

                            if (isMe) {
                                bubbleColor = 'var(--accent)'; // Cyan
                                textColor = '#000'; // Black text on Cyan
                                borderColor = 'var(--accent)';
                                align = 'flex-end'; // Right (Sent)
                                metaAlign = 'flex-end';
                            } else if (msg.role === 'admin') {
                                bubbleColor = 'rgba(0, 255, 127, 0.1)'; // Darker Neon Green base
                                borderColor = 'rgba(0, 255, 127, 0.4)'; // Brighter border
                                textColor = '#e0ffe0';
                            } else if (msg.role === 'analyst') {
                                bubbleColor = 'rgba(0, 191, 255, 0.1)'; // Darker Blue base
                                borderColor = 'rgba(0, 191, 255, 0.4)'; // Brighter border
                                textColor = '#e0f7ff';
                            }

                            return (
                                <div key={msg.id} style={{
                                    alignSelf: align,
                                    maxWidth: '75%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: metaAlign
                                }}>
                                    <div style={{ fontSize: '11px', color: '#666', marginBottom: '4px', display: 'flex', gap: '8px', padding: '0 4px' }}>
                                        <span style={{ fontWeight: 'bold', color: isMe ? 'var(--accent)' : (msg.role === 'admin' ? '#00ff7f' : (msg.role === 'analyst' ? '#00bfff' : '#aaa')) }}>
                                            {msg.user}
                                        </span>
                                        {/* <span style={{ opacity: 0.7 }}>{new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span> */}
                                    </div>
                                    <div style={{
                                        background: bubbleColor,
                                        color: textColor,
                                        border: `1px solid ${borderColor}`,
                                        padding: '10px 14px',
                                        borderRadius: '12px',
                                        borderTopLeftRadius: isMe ? '12px' : '2px', // Dynamic corner
                                        borderTopRightRadius: isMe ? '2px' : '12px',
                                        fontSize: '14px',
                                        lineHeight: 1.5,
                                        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }}>
                                        {formatMessage(msg.content, isMe)}
                                    </div>
                                    <div style={{ fontSize: '10px', color: '#444', marginTop: '2px', padding: '0 4px' }}>
                                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>

                {/* Input Area with Autocomplete */}
                <div style={{ position: 'relative' }}>
                    {showSuggestions && (
                        <div className="card animate-fade-in" style={{
                            position: 'absolute',
                            bottom: '100%',
                            left: '0',
                            width: '240px',
                            maxHeight: '200px',
                            overflowY: 'auto',
                            zIndex: 100,
                            padding: '0',
                            background: 'rgba(20, 20, 20, 0.95)',
                            border: '1px solid var(--accent)',
                            backdropFilter: 'blur(4px)'
                        }}>
                            {mentionableUsers
                                .filter(u => u.username.toLowerCase().includes(suggestionQuery.toLowerCase()))
                                .map(u => (
                                    <div
                                        key={u.username}
                                        onClick={() => insertMention(u.username)}
                                        style={{
                                            padding: '8px 12px',
                                            cursor: 'pointer',
                                            fontSize: '12px',
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            color: '#fff',
                                            borderBottom: '1px solid rgba(255, 255, 255, 0.05)'
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 255, 255, 0.1)'}
                                        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                    >
                                        <span style={{ fontWeight: 'bold' }}>{u.username}</span>
                                        <span style={{ opacity: 0.6, fontSize: '10px', textTransform: 'uppercase' }}>{u.role}</span>
                                    </div>
                                ))}
                        </div>
                    )}
                    <div className="flex gap-3">
                        <textarea
                            className="input"
                            rows={1}
                            value={note}
                            onChange={handleInputChange}
                            onClick={(e) => setCursorPos(e.target.selectionStart)}
                            onKeyUp={(e) => setCursorPos(e.target.selectionStart)}
                            placeholder="Type @ to tag..."
                            style={{ flex: 1, resize: 'none', minHeight: '42px' }}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    submitNote();
                                }
                            }}
                        />
                        <button
                            onClick={submitNote}
                            disabled={loading}
                            className="btn"
                            style={{ minWidth: '80px' }}
                        >
                            SEND
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
