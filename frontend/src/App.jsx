import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Rules from "./components/Rules";
import Login from "./components/Login";
import Register from "./components/Register";
import Settings from "./components/Settings";
import ResetPassword from "./components/ResetPassword";
import LandingPage from "./components/LandingPage"; // Import Landing
import { AuthProvider } from "./context/AuthContext";
import { EventsProvider } from "./context/EventsContext";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <AuthProvider>
      <EventsProvider>
        <Router>
          <Routes>
            <Route path="/" element={<LandingPage />} /> {/* New Landing */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route
              path="/dashboard" /* Moved from / */
              element={
                <ProtectedRoute>
                  <Dashboard apiBase="/api" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/rules"
              element={
                <ProtectedRoute>
                  <Rules apiBase="/api" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </EventsProvider>
    </AuthProvider>
  );
}
