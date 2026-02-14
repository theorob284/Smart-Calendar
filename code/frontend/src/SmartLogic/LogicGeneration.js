import { useState } from "react";
import AxiosInstance from "../Calendar/AxiosInstance";

export function useSmartPlan({ docID, onApplied }) {
  const [plan, setPlan] = useState(null);
  const [planning, setPlanning] = useState(false);
  const [useExisting, setUseExisting] = useState(true);
  const [allowReschedule, setAllowReschedule] = useState(false);
  const [maxTimeShift, setMaxTimeShift] = useState(60);

  const generatePlan = async () => {
    setPlanning(true);
    try {
      const res = await AxiosInstance.post("/api/smart/plan/", {GetDocumentIds: [Number(docID)],ExistingEvents: useExisting, AllowReschedule: allowReschedule, MaxTimeShift: maxTimeShift}); 
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

  return {plan, planning, useExisting, setUseExisting, allowReschedule, setAllowReschedule, maxTimeShift, setMaxTimeShift, generatePlan, applyPlan, clearPlan};
}