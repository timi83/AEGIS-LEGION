import React, { useContext, useState } from "react";
import axios from "axios";
import { AuthContext } from "../context/AuthContext";
import AssignPopover from "./AssignPopover";

export default function IncidentTable({ incidents = [], onView, apiBase = "/api" }) {
  const { token, user } = useContext(AuthContext);

  async function updateStatus(id, newStatus) {
    try {
      await axios.put(
        `${apiBase}/incidents/${id}/update-status?new_status=${newStatus}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch (e) {
      console.error("Status update failed:", e);
      alert("Failed to update status");
    }
  }

  // Popover State
  const [assignPopover, setAssignPopover] = useState(null); // { id: 123, x: 0, y: 0 }

  async function handleAssignClick(e, incident) {
    e.stopPropagation();
    // Only admins open the popover now (or if we want read-only popover later)
    if (user?.role !== 'admin') return;

    const rect = e.target.getBoundingClientRect();
    setAssignPopover({
      id: incident.id,
      x: rect.left + window.scrollX,
      y: rect.top + window.scrollY
    });
  }

  async function submitAssignment(incidentId, assignText) {
    try {
      await axios.post(`${apiBase}/incidents/${incidentId}/assign`,
        { assign_to: assignText },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAssignPopover(null);
    } catch (e) {
      alert("Assignment failed: " + (e.response?.data?.detail || e.message));
    }
  }

  // Sorting State
  const [sortConfig, setSortConfig] = React.useState({ key: 'timestamp', direction: 'desc' });

  const sortedIncidents = React.useMemo(() => {
    let sortableItems = [...incidents];
    if (sortConfig.key) {
      sortableItems.sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];

        // Custom Severity Sort
        if (sortConfig.key === 'severity') {
          const levels = { "critical": 4, "high": 3, "medium": 2, "low": 1 };
          aValue = levels[a.severity?.toLowerCase()] || 0;
          bValue = levels[b.severity?.toLowerCase()] || 0;
        }

        if (aValue < bValue) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableItems;
  }, [incidents, sortConfig]);

  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const SortIcon = ({ colKey }) => {
    if (sortConfig.key !== colKey) return <span style={{ opacity: 0.2 }}> ↕</span>;
    return <span>{sortConfig.direction === 'ascending' ? ' ↑' : ' ↓'}</span>;
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--panel-border)' }}>
            <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>ID</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Title</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Assignee</th>
            <th
              style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500, cursor: 'pointer' }}
              onClick={() => requestSort('alert_count')}
            >
              Count <SortIcon colKey="alert_count" />
            </th>
            <th
              style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500, cursor: 'pointer' }}
              onClick={() => requestSort('severity')}
            >
              Severity <SortIcon colKey="severity" />
            </th>
            <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Status</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Actions</th>
            <th
              style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500, cursor: 'pointer' }}
              onClick={() => requestSort('timestamp')}
            >
              Timestamp <SortIcon colKey="timestamp" />
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedIncidents.map((i) => (
            <tr key={i.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.03)' }}>
              <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', color: 'var(--accent)' }}>#{i.id}</td>
              <td style={{ padding: '12px 16px', fontWeight: 500 }}>{i.title}</td>

              {/* ASSIGNEE COLUMN */}
              <td style={{ padding: '12px 16px' }}>
                <div className="assignee-list" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  {i.assignees && i.assignees.length > 0 ? (
                    <>
                      {/* Avatar Stack (Max 3) */}
                      {i.assignees.slice(0, 3).map((a, idx) => (
                        <div
                          key={idx}
                          title={`${a.username} (${a.role})`}
                          className="assignee-avatar"
                          style={{
                            marginLeft: idx > 0 ? -8 : 0,
                            zIndex: 10 - idx,
                            border: '2px solid var(--panel-bg)',
                            cursor: user?.role === 'admin' ? 'pointer' : 'default'
                          }}
                          onClick={(e) => user?.role === 'admin' && handleAssignClick(e, i)}
                        >
                          {a.username.charAt(0).toUpperCase()}
                        </div>
                      ))}

                      {/* +N Badge */}
                      {i.assignees.length > 3 && (
                        <div
                          className="assignee-avatar"
                          style={{ marginLeft: -8, zIndex: 0, fontSize: 10, background: '#333' }}
                          onClick={(e) => user?.role === 'admin' && handleAssignClick(e, i)}
                        >
                          +{i.assignees.length - 3}
                        </div>
                      )}

                      {/* Admin Add Button */}
                      {user?.role === 'admin' && (
                        <button
                          onClick={(e) => handleAssignClick(e, i)}
                          style={{
                            background: 'none', border: 'none', color: 'var(--muted)',
                            cursor: 'pointer', fontSize: 14, marginLeft: 4
                          }}
                          title="Manage Assignments"
                        >+</button>
                      )}
                    </>
                  ) : (
                    <>
                      {/* Unassigned State */}
                      {user?.role === 'analyst' ? (
                        <button
                          onClick={(e) => submitAssignment(i.id, "me")} // Direct "Take"
                          className="btn-ghost"
                          style={{
                            padding: '2px 8px', fontSize: '10px',
                            border: '1px solid var(--accent)', color: 'var(--accent)',
                            background: 'rgba(0, 255, 180, 0.1)'
                          }}
                        >
                          ⚡ Take
                        </button>
                      ) : (
                        <button
                          onClick={(e) => handleAssignClick(e, i)}
                          className="btn-ghost"
                          style={{
                            padding: '2px 8px', fontSize: '10px',
                            border: '1px dashed var(--text-muted)', color: 'var(--text-muted)'
                          }}
                        >
                          + Assign
                        </button>
                      )}
                    </>
                  )}
                </div>
              </td>

              <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{i.alert_count || 1}</td>
              <td style={{ padding: '12px 16px' }}>
                <span className={`badge ${i.severity}`}>{i.severity}</span>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <select
                  value={i.status}
                  onChange={(e) => updateStatus(i.id, e.target.value)}
                  className="select"
                  style={{
                    padding: '4px 8px',
                    fontSize: '12px',
                    width: 'auto',
                    background: 'rgba(0,0,0,0.3)',
                    border: '1px solid',
                    borderColor:
                      (i.status?.toLowerCase() === 'open') ? '#00b8ff' :
                        (i.status?.toLowerCase() === 'investigating') ? '#d600ff' :
                          (i.status?.toLowerCase() === 'mitigated') ? '#00ffff' :
                            (i.status?.toLowerCase() === 'resolved') ? '#00ff9d' : '#444',
                    color:
                      (i.status?.toLowerCase() === 'open') ? '#00b8ff' :
                        (i.status?.toLowerCase() === 'investigating') ? '#d600ff' :
                          (i.status?.toLowerCase() === 'mitigated') ? '#00ffff' :
                            (i.status?.toLowerCase() === 'resolved') ? '#00ff9d' : '#888'
                  }}
                >
                  <option value="open">OPEN</option>
                  <option value="investigating">INVESTIGATING</option>
                  <option value="mitigated">MITIGATED</option>
                  <option value="resolved">RESOLVED</option>
                  <option value="closed">CLOSED</option>
                </select>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <button
                  onClick={() => onView(i)}
                  className="btn-ghost"
                  style={{ padding: '4px 12px', fontSize: '12px' }}
                >
                  VIEW
                </button>
              </td>
              <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-muted)' }}>
                {i.timestamp ? new Date(i.timestamp).toLocaleString() : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {assignPopover && (
        <AssignPopover
          incidentId={assignPopover.id}
          onAssign={(text) => submitAssignment(assignPopover.id, text)}
          onClose={() => setAssignPopover(null)}
          apiBase={apiBase}
          token={token}
          position={{ x: assignPopover.x, y: assignPopover.y }}
        />
      )}
    </div>
  );
}
