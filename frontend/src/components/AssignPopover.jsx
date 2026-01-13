import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function AssignPopover({ incidentId, onAssign, onClose, apiBase, token, position }) {
    const [input, setInput] = useState("");
    const [candidates, setCandidates] = useState([]); // Full list from server
    const [filteredCandidates, setFilteredCandidates] = useState([]);
    const [selectedUsers, setSelectedUsers] = useState([]); // Chips
    const [loading, setLoading] = useState(false);
    const [highlightedIndex, setHighlightedIndex] = useState(0);

    const inputRef = useRef(null);
    const dropdownRef = useRef(null);

    // 1. Fetch Candidates (Server Access + Admins)
    useEffect(() => {
        const fetchCandidates = async () => {
            setLoading(true);
            try {
                const res = await axios.get(`${apiBase}/incidents/${incidentId}/candidates`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setCandidates(res.data);
                setFilteredCandidates(res.data);
            } catch (e) {
                console.error("Failed to load candidates", e);
            } finally {
                setLoading(false);
            }
        };
        if (incidentId) fetchCandidates();
    }, [incidentId, apiBase, token]);

    // 2. Filter Candidates based on Input
    useEffect(() => {
        // Reset highlight when filter changes
        setHighlightedIndex(0);

        // Strip leading @ for search
        const rawInput = input.trim();
        const searchCanvas = rawInput.startsWith('@') ? rawInput.slice(1) : rawInput;

        if (!searchCanvas) {
            // Show all (except selected)
            setFilteredCandidates(candidates.filter(c => !selectedUsers.find(s => s.id === c.id)));
            return;
        }

        const q = searchCanvas.toLowerCase();
        const matches = candidates.filter(c =>
            (c.username.toLowerCase().includes(q) || c.role.toLowerCase().includes(q)) &&
            !selectedUsers.find(s => s.id === c.id) // Exclude already selected
        );
        setFilteredCandidates(matches);
    }, [input, candidates, selectedUsers]);

    // 3. Handlers
    const handleKeyDown = (e) => {
        if (e.key === 'Backspace' && !input && selectedUsers.length > 0) {
            // Remove last chip
            setSelectedUsers(prev => prev.slice(0, -1));
        }

        // Navigation
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setHighlightedIndex(prev => (prev + 1) % filteredCandidates.length);
        }
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            setHighlightedIndex(prev => (prev - 1 + filteredCandidates.length) % filteredCandidates.length);
        }

        if (e.key === 'Enter') {
            e.preventDefault();
            // If explicit match found or top suggestion?
            if (filteredCandidates.length > 0) {
                addChip(filteredCandidates[highlightedIndex]);
            }
        }
    };

    const addChip = (user) => {
        setSelectedUsers([...selectedUsers, user]);
        setInput("");
        inputRef.current?.focus();
    };

    const removeChip = (userId) => {
        setSelectedUsers(selectedUsers.filter(u => u.id !== userId));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (selectedUsers.length === 0) return;

        // Convert to payload expected by backend logic (list of strings or string)
        // Backend `_parse_assignment_input` handles list of strings.
        const payload = selectedUsers.map(u => `@${u.username}`);
        await onAssign(payload);
    };

    return (
        <div style={{
            position: 'absolute',
            top: position?.y + 30 || 100,
            left: position?.x - 150 > 0 ? position.x - 150 : 10, // Minimal boundary protection
            zIndex: 1000,
            background: 'rgba(20, 20, 30, 0.98)',
            border: '1px solid var(--accent)',
            borderRadius: '8px',
            padding: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.6)',
            width: '320px',
            backdropFilter: 'blur(12px)',
            animation: 'fadeIn 0.15s ease-out'
        }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, alignItems: 'center' }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--accent)', letterSpacing: '0.5px' }}>
                    ASSIGN TEAM
                </span>
                <button
                    onClick={onClose}
                    style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontSize: 16 }}
                >×</button>
            </div>

            <form onSubmit={handleSubmit}>
                {/* Chip Container + Input */}
                <div style={{
                    background: '#0a0a0a',
                    border: '1px solid #333',
                    borderRadius: '6px',
                    padding: '6px',
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '6px',
                    minHeight: '40px',
                    alignItems: 'center',
                    marginBottom: '8px'
                }} onClick={() => inputRef.current?.focus()}>

                    {selectedUsers.map(u => (
                        <div key={u.id} style={{
                            background: u.role === 'admin' ? 'rgba(0, 255, 180, 0.15)' : 'rgba(0, 184, 255, 0.15)',
                            border: `1px solid ${u.role === 'admin' ? 'var(--accent)' : '#00b8ff'}`,
                            borderRadius: '12px',
                            padding: '2px 8px',
                            fontSize: '12px',
                            color: '#eee',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                        }}>
                            {u.username}
                            <span
                                onClick={(e) => { e.stopPropagation(); removeChip(u.id); }}
                                style={{ cursor: 'pointer', opacity: 0.7, fontWeight: 'bold' }}
                            >×</span>
                        </div>
                    ))}

                    <input
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={selectedUsers.length === 0 ? "Search assigned users..." : ""}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'white',
                            flex: 1,
                            minWidth: '60px',
                            outline: 'none',
                            fontSize: '13px'
                        }}
                        autoFocus
                    />
                </div>

                {/* Suggestions List */}
                {loading ? (
                    <div style={{ padding: '12px', textAlign: 'center', color: '#666', fontSize: 12 }}>Loading users...</div>
                ) : (
                    <div style={{
                        maxHeight: '180px',
                        overflowY: 'auto',
                        border: filteredCandidates.length ? '1px solid #222' : 'none',
                        borderRadius: '4px',
                        background: '#111',
                        marginBottom: '12px',
                        display: 'block' // Always render container for messages
                    }} ref={dropdownRef}>
                        {filteredCandidates.length === 0 && (
                            <div style={{ padding: '8px', color: '#666', fontSize: 12, textAlign: 'center', fontStyle: 'italic' }}>
                                No matching users found.
                            </div>
                        )}

                        {filteredCandidates.map((u, i) => (
                            <div
                                key={u.id}
                                onClick={() => addChip(u)}
                                style={{
                                    padding: '8px 10px',
                                    fontSize: '12px',
                                    cursor: 'pointer',
                                    borderBottom: '1px solid #1a1a1a',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    background: i === highlightedIndex ? '#222' : 'transparent', // Highlight Logic
                                    transition: 'background 0.1s'
                                }}
                                onMouseEnter={() => setHighlightedIndex(i)}
                            >
                                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <span style={{
                                        width: 16, height: 16, borderRadius: '50%',
                                        background: u.role === 'admin' ? 'var(--accent)' : '#00b8ff',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        color: '#000', fontWeight: 'bold', fontSize: '10px'
                                    }}>{u.username[0].toUpperCase()}</span>
                                    <span style={{ color: '#eee' }}>{u.username}</span>
                                </span>
                                <span style={{
                                    color: '#666', fontSize: '9px', textTransform: 'uppercase',
                                    border: '1px solid #333', padding: '1px 4px', borderRadius: '4px'
                                }}>{u.role}</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Footer Actions */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                    <button
                        type="submit"
                        disabled={selectedUsers.length === 0}
                        className="btn"
                        style={{
                            padding: '6px 16px',
                            fontSize: 12,
                            opacity: selectedUsers.length === 0 ? 0.5 : 1,
                            cursor: selectedUsers.length === 0 ? 'not-allowed' : 'pointer'
                        }}
                    >
                        Assign {selectedUsers.length > 0 ? `(${selectedUsers.length})` : ''}
                    </button>
                </div>
            </form>
        </div>
    );
}
