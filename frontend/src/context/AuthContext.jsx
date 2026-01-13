import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from "jwt-decode";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);

    const fetchUser = async () => {
        try {
            // Set default from token first to avoid flicker
            const decoded = jwtDecode(token);
            // setUser(decoded); // Optional: Set partial data

            // Fetch full profile
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            const res = await axios.get('/api/me');
            setUser(res.data);
        } catch (error) {
            console.error("Failed to fetch user profile", error);
            // If API fails (e.g. 401), logout
            if (error.response && error.response.status === 401) {
                logout();
            }
        }
    };

    useEffect(() => {
        if (token) {
            localStorage.setItem('token', token);
            fetchUser();
        } else {
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
            setUser(null);
        }
    }, [token]);

    const login = (newToken) => {
        setToken(newToken);
    };

    const logout = () => {
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, refreshUser: fetchUser }}>
            {children}
        </AuthContext.Provider>
    );
};
