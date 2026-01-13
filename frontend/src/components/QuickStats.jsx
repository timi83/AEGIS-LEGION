import React from "react";

export default function QuickStats({ incidents, statusMsg }) {
  return (
    <div className="card" style={{marginBottom:12}}>
      <h3 className="header" style={{color:"var(--muted)"}}>Quick Stats</h3>
      <div style={{marginTop:10}}>
        <div>Total incidents: <strong>{incidents.length}</strong></div>
        <div>Open: {incidents.filter(i=>i.status==="open").length}</div>
        <div>High severity: {incidents.filter(i=>i.severity==="high").length}</div>
        <div style={{marginTop:10,color:"var(--muted)"}}>Status: {statusMsg}</div>
      </div>
    </div>
  );
}
