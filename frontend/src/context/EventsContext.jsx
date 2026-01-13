import React, { createContext, useState, useEffect, useContext } from 'react';
import { AuthContext } from './AuthContext';

export const EventsContext = createContext();

export const EventsProvider = ({ children, apiBase = "/api" }) => {
    const { token } = useContext(AuthContext);
    const [lastEvent, setLastEvent] = useState(null);
    const [status, setStatus] = useState("disconnected");

    useEffect(() => {
        if (!token) return;

        console.log("🔌 Connecting to Event Stream...");
        const es = new EventSource(`${apiBase}/events/stream?token=${token}`);

        es.onopen = () => {
            console.log("✅ Event Stream Connected");
            setStatus("connected");
        };

        es.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // console.log("⚡ Event:", data.type);
                setLastEvent(data); // Broadcast to consumers
            } catch (e) {
                console.error("SSE Parse Error", e);
            }
        };

        es.onerror = (err) => {
            // console.warn("SSE Error", err);
            setStatus("error");
            es.close();
            // Retry handled by browser or manual? Browser retries usually.
        };

        return () => {
            es.close();
            setStatus("disconnected");
        };
    }, [token, apiBase]);

    return (
        <EventsContext.Provider value={{ lastEvent, status }}>
            {children}
        </EventsContext.Provider>
    );
};
