import React from "react";
import { useSmartPlan } from "./LogicGeneration";

export default function SmartPlanUI({ docID, onApplied }) {
  const {plan, planning, useExisting, setUseExisting,generatePlan, applyPlan, clearPlan } = useSmartPlan({ docID, onApplied });

  return (
    <div style={{ marginTop: 12 }}>
      <label> 
        <input type="checkbox" checked={useExisting} onChange={(e) => setUseExisting(e.target.checked)}/> Respect existing events
      </label>

      <button onClick={generatePlan} disabled={planning} style={{ marginLeft: 8 }}> {planning ? "Planning..." : "Generate Smart Plan"}</button>

      {plan && (
        <div style={{ marginTop: 12, padding: 8, border: "1px solid #ccc" }}>
          <p><b>Smart Plan</b></p>
          <p>Selected: {plan.stats?.selected_count ?? plan.selected?.length ?? 0}</p>
          <p>Skipped: {plan.stats?.skipped_count ?? plan.skipped?.length ?? 0}</p>

          <button onClick={applyPlan}>Apply Smart Build</button>
          <button onClick={clearPlan} style={{ marginLeft: 8 }}>Clear</button>
        </div>
      )}
    </div>
  );
}