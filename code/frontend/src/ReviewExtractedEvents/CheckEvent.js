import React, { useState, useEffect, useCallback } from "react";
import AxiosInstance from "../Calendar/AxiosInstance";
import { useParams, useNavigate } from "react-router-dom";
import SmartPlanPanel from "../SmartLogic/SmartUI";

export default function CheckExtractedEvent() {
  const navigate = useNavigate();
  const { docID } = useParams();

  const [checkevent, setCheckEvent] = useState([]);
  const [createdevents, setCreatedEvents] = useState([]);
  const [conflictbyid, setConflictById] = useState({});

  const [accepting, setAccepting] = useState(false);
  const [counter, setCounter] = useState(0);

  const [rejecting, setRejecting] = useState(false);
  const [counterRej, setRejCounter] = useState(0);

  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({
    title: "",
    start_time: "",
    end_time: "",
    location: "",
    description: "",
  });

  const GetData = useCallback(() => {AxiosInstance.get(`/api/candidates/?document=${docID}&status=PENDING`).then((res) => {setCheckEvent(res.data);});}, [docID]);

  useEffect(() => {GetData();}, [GetData]);
  useEffect(() => {AxiosInstance.get(`/api/events/`).then((res) => {setCreatedEvents(res.data);});}, []);

  const CheckConflict = () => {
    const result = {};

    for (const pending of checkevent) {
      if (!pending.start_time || !pending.end_time) {
        result[pending.id] = 0;
        continue;
      }

      const pendingStart = new Date(pending.start_time).getTime();
      const pendingEnd = new Date(pending.end_time).getTime();

      let conflictCounter = 0;

      for (const events of createdevents) {
        if (!events.start_time || !events.end_time) continue;
        const eventStart = new Date(events.start_time).getTime();
        const eventEnd = new Date(events.end_time).getTime();

        const conflict = pendingStart < eventEnd && pendingEnd > eventStart;

        if (conflict) conflictCounter += 1;
      }

      for (const pend of checkevent) {
        if (pend.id === pending.id ||!pend.start_time ||!pend.end_time) continue;

        const selfPendStart = new Date(pend.start_time).getTime();
        const selfPendEnd = new Date(pend.end_time).getTime();

        const pendConflict = pendingStart < selfPendEnd && pendingEnd > selfPendStart;
        if (pendConflict) conflictCounter += 1;
      }

      result[pending.id] = conflictCounter;
    }
    setConflictById(result);
  };

  useEffect(() => {CheckConflict();}, [checkevent, createdevents]);

  const updateStatus = (id) => {
    setCheckEvent((prev) => {
      const updated = prev.filter((c) => c.id !== id);
      if (updated.length === 0) {
        navigate("/");
      }
      return updated;
    });
  };

  const accept = async (id) => {
    await AxiosInstance.post(`/api/candidates/${id}/accept/`);
    updateStatus(id);
  };

  const reject = async (id) => {
    await AxiosInstance.post(`/api/candidates/${id}/reject/`);
    updateStatus(id);
  };

  const AcceptAll = async () => {
    setAccepting(true);
    setCounter(0);

    for (const cand of checkevent) {
      await AxiosInstance.post(`/api/candidates/${cand.id}/accept/`);
      setCounter((prev) => prev + 1);
      updateStatus(cand.id);
    }
    setAccepting(false);
  };

  const RejectAll = async () => {
    setRejecting(true);
    setRejCounter(0);

    for (const cand of checkevent) {
      await AxiosInstance.post(`/api/candidates/${cand.id}/reject/`);
      setRejCounter((prev) => prev + 1);
      updateStatus(cand.id);
    }
    setRejecting(false);
  };

  const edit = async (id) => {
    await AxiosInstance.patch(`/api/candidates/${id}/`, {
      title: form.title,
      start_time: form.start_time,
      end_time: form.end_time,
      location: form.location,
      description: form.description,
    });

    GetData();
    setEditId(null);
  };

  const handleSmartApplied = async () => {
    GetData();
    const eventRes = await AxiosInstance.get("/api/events/");
    setCreatedEvents(eventRes.data);
  };

  return (
    <div>
      <h1>Check Event</h1>

      <div>
        <button onClick={AcceptAll} disabled={accepting}>Accept all Events</button>
        {accepting && (<p>Processing {counter} of {checkevent.length}</p>)}

        <button onClick={RejectAll} disabled={rejecting}>Reject all Events</button>
        {rejecting && (<p>Processing {counterRej} of {checkevent.length}</p>)}
      </div>

      <SmartPlanPanel docID={docID}onApplied={handleSmartApplied}/>

      {checkevent.map((c) => (
        <div key={c.id} style={{ marginTop: 16 }}>
          {editId === c.id ? (
            <div>
              <input value={form.title} onChange={(e) =>setForm({ ...form, title: e.target.value })}/>
              <input type="datetime-local" value={form.start_time} onChange={(e) =>setForm({ ...form, start_time: e.target.value })}/>
              <input type="datetime-local" value={form.end_time} onChange={(e) =>setForm({ ...form, end_time: e.target.value })}/>
              <input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })}/>
              <input value={form.description} onChange={(e) =>setForm({ ...form, description: e.target.value })}/>

              <button onClick={() => edit(c.id)}>Save</button>
              <button onClick={() => setEditId(null)}>Cancel</button>
            </div> ) : (
            <div>
              <p>{c.title}</p>
              <p>{c.start_time}</p>
              <p>{c.end_time}</p>
              <p>{c.location}</p>
              <p>{c.raw_text}</p>
              <p>Conflicts: {conflictbyid[c.id] ?? 0}</p>

              <button onClick={() => accept(c.id)}>Accept</button>

              <button onClick={() => {
                  setEditId(c.id);
                  setForm({
                    title: c.title || "",
                    start_time: (c.start_time || "").replace("Z", "").slice(0, 16),
                    end_time: (c.end_time || "").replace("Z", "").slice(0, 16),
                    location: c.location || "",
                    description: c.description || c.raw_text || "",
                  }); }}>Edit </button>

              <button onClick={() => reject(c.id)}>Reject</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}