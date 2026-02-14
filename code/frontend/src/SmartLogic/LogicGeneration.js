import { useState } from "react";
import AxiosInstance from "../Calendar/AxiosInstance";

export function useSmartPlan({ docID, onApplied }) {
  const [plan, setPlan] = useState(null);
  const [planning, setPlanning] = useState(false);
  const [useExisting, setUseExisting] = useState(true);

  const generatePlan = async () => {
    setPlanning(true);
    try {
      const res = await AxiosInstance.post("/api/smart/plan/", {GetDocumentIds: [Number(docID)],ExistingEvents: useExisting,});
      setPlan(res.data);
    } finally { setPlanning(false);}
  };

  const applyPlan = async () => {
    if (!plan?.selected?.length) return;

    for (const item of plan.selected) {
        await AxiosInstance.post(`/api/candidates/${item.candidate_id}/accept/`);
    }
    setPlan(null);
    if (onApplied) await onApplied();
  };
  const clearPlan = () => setPlan(null);

  return {plan, planning, useExisting, setUseExisting, generatePlan, applyPlan, clearPlan};
}