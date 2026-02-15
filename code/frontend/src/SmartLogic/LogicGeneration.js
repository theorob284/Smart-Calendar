import { useState } from "react";
import AxiosInstance from "../Calendar/AxiosInstance";

export function useSmartPlan({ docID, onApplied }) {
  const [plan, setPlan] = useState(null);
  const [planning, setPlanning] = useState(false);
  const [useExisting, setUseExisting] = useState(true);
  const [allowReschedule, setAllowReschedule] = useState(false);
  const [maxTimeShift, setMaxTimeShift] = useState(60);
  const [strictness, setStrictness] = useState(1)
  const [useWorkHours, setUseWorkHours] = useState(true)
  const [workStartHour, setWorkStartHour] = useState(9);
  const [workEndHour, setWorkEndHour] = useState(17);
  const [avoidWeekend, setAvoidWeekend] = useState(true)
  const [bufferMinutes, setBufferMinutes] = useState(10);
  const [bufferPenalty, setBufferPenalty] = useState(3.0);

  const generatePlan = async () => {
    setPlanning(true)
    let conflictPenalty = 1.0;
    let movePenalty = 0.05;
    let skipPenalty = 2.0;
    let outsideWorkPenalty = 5.0;
    let weekendPenalty = 10.0;

    if (strictness === 0){
        conflictPenalty = 0.5;
        movePenalty = 0.02;
        skipPenalty = 3.0;
        outsideWorkPenalty = 1.0;
        weekendPenalty = 2.0;
    }

    if (strictness === 2) {
        conflictPenalty = 2.5;
        movePenalty = 0.1;
        skipPenalty = 1.0;
        outsideWorkPenalty = 15.0;
        weekendPenalty = 25.0;
    }

    try {
      const res = await AxiosInstance.post("/api/smart/plan/", {GetDocumentIds: [Number(docID)],ExistingEvents: useExisting, AllowReschedule: allowReschedule, MaxTimeShift: maxTimeShift, ConflictPenalty: conflictPenalty, 
            MovePenalty: movePenalty, SkipPenalty: skipPenalty, outsideWorkPenalty, weekendPenalty,
            WorkStart: workStartHour, WorkEnd: workEndHour, AvoidWeekends: avoidWeekend, WorkHours: useWorkHours,
            BufferMinutes: bufferMinutes, BufferPenalty: bufferPenalty,}); 
      setPlan(res.data);
    } finally { setPlanning(false);}
  };

  const applyPlan = async () => {
    if (!plan?.selected?.length) return;

    for (const item of plan.selected) {
        await AxiosInstance.post(`/api/candidates/${item.candidate_id}/accept/`, {start_time: item.start_time, end_time: item.end_time});
    }
    setPlan(null);
    if (onApplied) await onApplied();
  };
  const clearPlan = () => setPlan(null);

  return {plan, planning, useExisting, setUseExisting, allowReschedule, setAllowReschedule, maxTimeShift, setMaxTimeShift, generatePlan, applyPlan, clearPlan, strictness, setStrictness, 
        workStartHour, workEndHour, setWorkStartHour, setWorkEndHour, avoidWeekend, setAvoidWeekend, useWorkHours, setUseWorkHours, bufferMinutes, setBufferMinutes, bufferPenalty, setBufferPenalty};
}