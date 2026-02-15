import React from "react";
import { useSmartPlan } from "./LogicGeneration";

export default function SmartPlanUI({ docID, onApplied }) {
  const {plan, planning, useExisting, setUseExisting, allowReschedule, setAllowReschedule, maxTimeShift, setMaxTimeShift, generatePlan, applyPlan, clearPlan, strictness, setStrictness,
    workStartHour, workEndHour, setWorkEndHour, setWorkStartHour, avoidWeekend, setAvoidWeekend, useWorkHours, setUseWorkHours, bufferMinutes, setBufferMinutes, bufferPenalty, setBufferPenalty,
   } = useSmartPlan({ docID, onApplied });

  return (
    <div style={{  marginTop: 10, padding: 8, border: "1px dashed #ccc" }}>
       <b>Preferences</b>
       <br></br>
      <label> 
        <input type="checkbox" checked={useExisting} onChange={(e) => setUseExisting(e.target.checked)}/> Respect existing events
      </label>

      <div style={{ marginTop: 8 }}>
        <label>
            <input type="checkbox" checked={allowReschedule} onChange={(e) => setAllowReschedule(e.target.checked)}/>{" "}Allow rescheduling extracted events
        </label>
        
        <span style={{ marginLeft: 10 }}> Max shift (mins):{" "}
          <input type="number" min={0} max={1440} value={maxTimeShift} onChange={(e) => setMaxTimeShift(Number(e.target.value))} disabled={!allowReschedule} style={{ width: 90 }} />
        </span>
      </div>

      <div style={{ marginTop: 12 }}>
        <label>Strictness:</label>
        <input type="range" min="0" max="2" step="1" value={strictness} onChange={(e) => setStrictness(Number(e.target.value))} style={{ marginLeft: 10 }}/>
        <span style={{ marginLeft: 10 }}>
          {strictness === 0 && "Aggressive"}
          {strictness === 1 && "Balanced"}
          {strictness === 2 && "Strict"}
        </span>
      </div>

      <div>
        <label>
            <input type="checkbox" checked={useWorkHours} onChange={(e) => setUseWorkHours(e.target.checked)} />{" "} Use working hours
        </label>

        <div style={{ marginTop: 8 }}>
            <label style={{ marginRight: 8 }}>Work hours:</label>
            <input type="number" min={0} max={23} value={workStartHour} onChange={(e) => setWorkStartHour(Number(e.target.value))} style={{ width: 60 }} disabled={!useWorkHours} />
            <span style={{ margin: "0 6px" }}>to</span>
            <input type="number" min={1} max={24} value={workEndHour} onChange={(e) => setWorkEndHour(Number(e.target.value))} style={{ width: 60 }} disabled={!useWorkHours}/>
        </div>

        <div style={{ marginTop: 8 }}>
            <label>
            <input type="checkbox" checked={avoidWeekend} onChange={(e) => setAvoidWeekend(e.target.checked)} disabled={!useWorkHours} />{" "} Avoid weekends </label>
        </div>
      </div>
       
       <div style={{ marginTop: 12 }}>
            <label style={{ marginRight: 8 }}>Event buffer (mins):</label>
            <input type="number" min={0} max={120} value={bufferMinutes} onChange={(e) => setBufferMinutes(Number(e.target.value))} style={{ width: 60 }}/>
            <span style={{ marginLeft: 12 }}>
                <label style={{ marginRight: 8 }}>Buffer penalty:</label> <input type="number" step="0.5" min={0} value={bufferPenalty} onChange={(e) => setBufferPenalty(Number(e.target.value))}style={{ width: 70 }} />
            </span>
      </div>

      <button onClick={generatePlan} disabled={planning} style={{ marginLeft: 8 }}> {planning ? "Planning..." : "Generate Smart Plan"}</button>

      {plan && (
        <div style={{ marginTop: 12, padding: 8, border: "1px solid #ccc" }}>
          <p><b>Smart Plan</b></p>
          <p>Selected: {plan.stats?.selected_count ?? plan.selected?.length ?? 0}</p>
          <p>Skipped: {plan.stats?.skipped_count ?? plan.skipped?.length ?? 0}</p>

          {plan.selected?.length > 0 && (
            <div style={{ marginTop: 12 }}>
                <h4>Selected Events</h4>
                {plan.selected?.map((item) => (
                <div key={item.candidate_id} style={{ marginBottom: 8 }}>
                    <strong>{item.title}</strong>
                    <div>
                        {new Date(item.start_time).toLocaleString()} →{" "}
                        {new Date(item.end_time).toLocaleString()}
                    </div>
                    <div> Moved: {item.moved_minutes} mins </div>
                    <div style={{fontSize: 12, color: "#666"}}>
                        Overlap(existing): {item.explanation?.existing_overlap_minutes ?? 0} mins {" | "}
                        Overlap(selected): {item.explanation?.selected_overlap_minutes ?? 0} mins{" | "}
                        Score: {item.explanation?.score?.toFixed(2)}
                    </div>
                
                    {item.alternatives?.length > 0 && (
                    <div style={{ marginTop: 6, fontSize: 12 }}>
                        <div style={{ fontWeight: "bold" }}>Alternatives:</div>

                        {item.alternatives.map((alt, idx) => (
                        <div key={idx} style={{ marginTop: 2 }}>
                            {new Date(alt.start).toLocaleString()} →{" "}
                            {new Date(alt.end).toLocaleString()}{" "}
                            (moved {alt.moved} mins, score {Number(alt.score).toFixed(2)})
                        </div>
                        ))}
                    </div>
                    )}
                </div>
                ))}
            </div>
            )}

          <button onClick={applyPlan}>Apply Smart Build</button>
          <button onClick={clearPlan} style={{ marginLeft: 8 }}>Clear</button>
        </div>
      )}
    </div>
  );
}