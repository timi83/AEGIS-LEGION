import axios from "axios";
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

import "./index.css";
import "./App.css";
import "./styles.css";

// Set base URL for production config
if (import.meta.env.VITE_API_URL) {
    axios.defaults.baseURL = import.meta.env.VITE_API_URL;
}

createRoot(document.getElementById("root")).render(<App />);
