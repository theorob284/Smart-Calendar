import React from "react";
import { useSmartPlan } from "./LogicGeneration";
import "../CSS/SmartPlan.css";

export default function SmartPlanUI({ docID, onApplied }) {
  const {plan, planning, useExisting, setUseExisting, allowReschedule, setAllowReschedule, maxTimeShift, setMaxTimeShift, generatePlan, applyPlan, clearPlan, strictness, setStrictness,
    workStartHour, workEndHour, setWorkEndHour, setWorkStartHour, avoidWeekend, setAvoidWeekend, useWorkHours, setUseWorkHours, bufferMinutes, setBufferMinutes, ChooseAlternative
   } = useSmartPlan({ docID, onApplied });

  return (
  <div className="smartPlan">
    <p className="smartPlanTitle">Preferences</p>
    <div className="smartRow">
      <label>
        <input type="checkbox" checked={useExisting} onChange={(e) => setUseExisting(e.target.checked)}/>Respect existing events
      </label>
    </div>

    <div className="smartRow">
      <label>
        <input type="checkbox" checked={allowReschedule} onChange={(e) => setAllowReschedule(e.target.checked)}/>Allow rescheduling extracted events
      </label>

      <span className="smartSub">Max shift (mins):</span>
      <input className="smartInput" type="number" min={0} max={1440} value={maxTimeShift} disabled={!allowReschedule} onChange={(e) => { 
        let value = Number(e.target.value);
        value = Math.max(0, Math.min(1440, value))
        setMaxTimeShift(value)}}/>
    </div>

    <div className="smartRow">
      <label>
        <input type="checkbox" checked={useWorkHours} onChange={(e) => setUseWorkHours(e.target.checked)}/> Use working hours
      </label>
    </div>

    <div className="smartRow">
      <span className="smartSub">Work hours:</span>
      <input className="smartInput" type="number" min={0} max={23} value={workStartHour} disabled={!useWorkHours} onChange={(e) => { 
        let value = Number(e.target.value);
        value = Math.max(0, Math.min(23, value));
        if (value >= workEndHour){
          value = workEndHour - 1
        }
        setWorkStartHour(value)} 
        }/>
      <span className="smartSub">to</span>
      <input className="smartInput" type="number" min={1} max={24} value={workEndHour} disabled={!useWorkHours} onChange={(e) => {
        let value = Number(e.target.value);
        value = Math.max(0, Math.min(23, value));
        if (value <= workStartHour) {
          value = workStartHour + 1
        }
        setWorkEndHour(value)}} />
    </div>

    <div className="smartRow">
      <label>
        <input type="checkbox" checked={avoidWeekend} onChange={(e) => setAvoidWeekend(e.target.checked)} disabled={!useWorkHours}/>Avoid weekends
      </label>
    </div>

    <div className="smartRow">
      <span className="smartSub">Event buffer (mins):</span>
      <input className="smartInput" type="number" min={0} max={160} value={bufferMinutes} onChange={(e) => { 
        let value = Number(e.target.value);
        if (value > 160) value = 160
        if (value < 0) value = 0
        setBufferMinutes(value)}}/>
    </div>

    <div className="smartRow">
      <span className="smartSub">Strictness:</span>
      <input className="smartRange" type="range" min="0" max="2" step="1" value={strictness} onChange={(e) => setStrictness(Number(e.target.value))}/>
      <span className="smartSub">
        {strictness === 0 && "Light"}
        {strictness === 1 && "Balanced"}
        {strictness === 2 && "Strict"}
      </span>
    </div>

    <div className="smartActions">
      <button className="smartBtnPrimary" onClick={generatePlan} disabled={planning}> {planning ? "Planning..." : "Generate Smart Plan"} </button>
    </div>

      {plan && (
        <div className="planBox">
          <div className="planHeader">
            <h4>Smart Plan</h4>
            <div className="planStats">
              <span>Events -</span>
              <span>Selected: {plan.stats?.selected_count ?? plan.selected?.length ?? 0}</span>
              <span>Skipped: {plan.stats?.skipped_count ?? plan.skipped?.length ?? 0}</span>
            </div>
          </div>

          {plan.selected?.length > 0 && (<>
              <div className="planSectionTitle">Selected Events</div>

              {plan.selected.map((item) => (
                <div key={item.candidate_id} className="planItem">
                  <p className="planItemTitle">{item.title}</p>

                  <p className="planItemTime">
                    {new Date(item.start_time).toLocaleString()} →{" "}
                    {new Date(item.end_time).toLocaleString()}
                  </p>

                  <p className="planItemMeta">
                    <span className="badge">Moved: {item.moved_minutes} mins</span>
                    <span className="badge">Overlap(existing): {item.explanation?.existing_overlap_minutes ?? 0}m</span>
                    <span className="badge">Overlap(selected): {item.explanation?.selected_overlap_minutes ?? 0}m</span>
                    <span className="badge">Score: {item.explanation?.score?.toFixed(2)}</span>
                  </p>

                  {item.alternatives?.length > 0 && (
                    <div className="altWrap">
                      <p className="altTitle">Alternatives</p>

                      {item.alternatives.map((alt, idx) => {
                        const isChosen =
                          new Date(item.start_time).getTime() === new Date(alt.start).getTime() &&
                          new Date(item.end_time).getTime() === new Date(alt.end).getTime();

                        return (
                          <button key={idx} type="button" onClick={() => ChooseAlternative(item.candidate_id, alt)} className={`altBtn ${isChosen ? "altBtnChosen" : ""}`}>
                            {new Date(alt.start).toLocaleString()} →{" "}
                            {new Date(alt.end).toLocaleString()} (moved {alt.moved}m, score{" "}
                            {Number(alt.score).toFixed(2)})
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              ))}</>
          )}

          <div className="planActions">
            <button className="smartBtnPrimary" onClick={applyPlan}> Apply Smart Build</button>
            <button className="smartBtnGhost" onClick={clearPlan}> Clear</button>
          </div>
        </div>
            )}
    </div>
  );
}