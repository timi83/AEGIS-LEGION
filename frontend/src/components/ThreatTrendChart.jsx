import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  TimeScale,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, TimeScale, Tooltip, Legend);

export default function ThreatTrendChart({ incidents = [] }) {
  // Aggregate incidents by minute
  const now = Date.now();
  const buckets = {};
  const labels = [];

  // Initialize last 10 minutes buckets
  for (let i = 9; i >= 0; i--) {
    const t = new Date(now - i * 60000);
    const key = t.getHours() + ":" + t.getMinutes();
    buckets[key] = 0;
    labels.push(t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
  }

  // Count incidents
  (incidents || []).forEach(inc => {
    if (!inc.timestamp) return;

    // Fix: Backend sends naive UTC string (e.g., "2023-11-20T10:00:00")
    // Browser treats this as Local Time. We must treat it as UTC.
    let tsString = inc.timestamp;
    if (tsString.indexOf('Z') === -1 && tsString.indexOf('+') === -1) {
      tsString += 'Z';
    }

    const t = new Date(tsString);

    // Only count if within last 10 minutes
    const diff = now - t.getTime();
    if (diff >= 0 && diff < 10 * 60000) {
      const key = t.getHours() + ":" + t.getMinutes();
      if (buckets[key] !== undefined) {
        buckets[key]++;
      }
    }
  });

  const counts = Object.values(buckets);

  const data = {
    labels,
    datasets: [
      {
        label: "Events / min",
        data: counts,
        tension: 0.3,
        fill: true,
        backgroundColor: "rgba(0,208,255,0.06)",
        borderColor: "rgba(0,208,255,0.9)",
        pointRadius: 2
      }
    ]
  };

  const options = {
    plugins: { legend: { display: false } },
    scales: {
      y: { ticks: { color: "#9fb8c9" }, grid: { color: "rgba(255,255,255,0.03)" } },
      x: { ticks: { color: "#9fb8c9" }, grid: { color: "transparent" } }
    },
    maintainAspectRatio: false
  };

  return <div style={{ height: 120 }}><Line data={data} options={options} /></div>;
}
