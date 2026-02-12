import React, { useState, useEffect, useCallback } from 'react'
import AxiosInstance from '../Calendar/AxiosInstance'
import {useParams} from "react-router-dom"
import { useNavigate } from 'react-router-dom'

export default function CheckExtractedEvent() {

    const navigate = useNavigate();
    const [checkevent, setCheckEvent] = useState([]);
    const [accepting, setAccepting] = useState(false);
    const [counter, setCounter] = useState(0);
    const [rejecting, setRejecting] = useState(false);
    const [counterRej, setRejCounter] = useState(0);
    const [conflictbyid, setConflictById] = useState({});
    const {docID} = useParams();
    const [editId, setEditId] = useState(null);
    const [createdevents, setCreatedEvents] = useState([]);
    const [form, setForm] = useState({
      title: "",
      start_time: "",
      end_time: "",
      location: "",
      description: ""
    });

    //smart generation
    const [plan, setPlan] = useState(null);
    const [planning, setPlanning] = useState(false)
    const [useExisting, setUseExisting] = useState(true)

    const GetData = useCallback(() => {
      AxiosInstance.get(`/api/candidates/?document=${docID}&status=PENDING`).then((res) => { 
        setCheckEvent(res.data);});
      }, [docID]);

    
    const CheckConflict = () => {
      const result = {};
      for (const pending of checkevent){
      
        if (!pending.start_time || !pending.end_time) {
          result[pending.id] = 0;
          continue
        }
        const pendingStart = new Date(pending.start_time).getTime();
        const pendingEnd = new Date(pending.end_time).getTime();

        let conflictCounter = 0;
        for (const events of createdevents) {
          if (!events.start_time || !events.end_time) continue;

          const eventStart = new Date(events.start_time).getTime();
          const eventEnd = new Date(events.end_time).getTime();

          const conflict = pendingStart < eventEnd && pendingEnd > eventStart;
          if (conflict) {
            conflictCounter += 1;
          } 
        }

        for (const pend of checkevent){
          if (pend.id === pending.id || !pend.start_time || !pend.end_time ){
            continue;
          } 
          const selfPendStart = new Date(pend.start_time).getTime();
          const selfPendEnd = new Date(pend.end_time).getTime();

          const pendConflict = pendingStart < selfPendEnd && pendingEnd > selfPendStart;

          if (pendConflict){
            conflictCounter += 1;
          }
        }
        
        result[pending.id] = conflictCounter;
      }

      setConflictById(result);
    }
    useEffect(() => {GetData();}, [GetData]);
    useEffect(() => {AxiosInstance.get(`/api/events/`).then((res) => {setCreatedEvents(res.data);});}, []);
    useEffect(() => {CheckConflict();}, [checkevent, createdevents]);

    const updateStatus = (id) => {
      setCheckEvent(prev => {const updated = prev.filter(c => c.id !== id);
      if (updated.length === 0) {
        navigate("/");
      }
      return updated; });
    };

    const accept = async (id) => {
      await AxiosInstance.post(`/api/candidates/${id}/accept/`)
      updateStatus(id);
    }

    const AcceptAll = async () => {
      setAccepting(true);
      setCounter(0);
      
      for (const cand of checkevent){

        const id = cand.id
        await AxiosInstance.post(`/api/candidates/${id}/accept/`)
        setCounter(prev => prev + 1);
        updateStatus(id);
      }

      setAccepting(false);
    }

    const RejectAll = async () => {
      setRejecting(true);
      setRejCounter(0);
      
      for (const cand of checkevent){

        const id = cand.id
        await AxiosInstance.post(`/api/candidates/${id}/reject/`)
        setRejCounter(prev => prev + 1);
        updateStatus(id);
      }

      setRejecting(false);
    }

    const edit = async (id) => {
      await AxiosInstance.patch(`/api/candidates/${id}/`, {
        title: form.title,
        start_time: form.start_time,
        end_time: form.end_time,
        location: form.location,
        description: form.description
      })

      GetData()
      setEditId(null)
    }

    const reject = async (id) => {
      await AxiosInstance.post(`/api/candidates/${id}/reject/`)
      updateStatus(id);
    }

    const generatePlan = async () => {
      setPlanning(true);

      const res = await AxiosInstance.post("/api/smart/plan/", {GetDocumentIds: [Number(docID)], ExistingEvents: useExisting})
      setPlan(res.data);
      setPlanning(false);
    }

    const applyPlan = async () => {
      if (!plan?.selected) return;

      for (const item of plan.selected) {
        await AxiosInstance.post(`/api/candidates/${item.candidate_id}/accept/`);
      }

      await GetData();
      const eventRes = await AxiosInstance.get("/api/events/");
      setCreatedEvents(eventRes.data);
      setPlan(null);
    }

    return (
      <div>
        <h1>Check Event</h1>

        <div>
          <button onClick={AcceptAll} disabled = {accepting} >Accept all Events</button>
          {accepting && (<><p>Processing {counter} of {checkevent.length}</p></>)}

          <button onClick={RejectAll} disabled = {rejecting} >Reject all Events</button>
          {rejecting && (<><p>Processing {counterRej} of {checkevent.length}</p></>)}
        </div>

        <div style={{ marginTop: 12 }}>
          <label>
            <input type="checkbox" checked={useExisting} onChange={(e) => setUseExisting(e.target.checked)}/>Respect existing events
          </label>

          <button onClick={generatePlan} disabled={planning}>
            {planning ? "Planning..." : "Generate Smart Plan"}
          </button>

          {plan && (
            <div style={{ marginTop: 12, padding: 8, border: "1px solid #ccc" }}>
              <p><b>Smart Plan</b></p>
              <p>Selected: {plan.stats?.selected_count ?? plan.selected?.length ?? 0}</p>
              <p>Skipped: {plan.stats?.skipped_count ?? plan.skipped?.length ?? 0}</p>

              <button onClick={applyPlan}>Apply Smart Build</button>
              <button onClick={() => setPlan(null)}>Clear</button>
            </div>
          )}
        </div>

        {checkevent.map(c => (
          <div key={c.id}>


            {editId === c.id ? (
              <div>
                <input value={form.title} onChange={e => setForm({...form, title: e.target.value})}/>
                <input type="datetime-local" value={form.start_time} onChange={e => setForm({...form, start_time: e.target.value})}/>
                <input type="datetime-local" value={form.end_time}onChange={e => setForm({...form, end_time: e.target.value})}/>
                <input value={form.location}onChange={e => setForm({...form, location: e.target.value})}/>
                <input value={form.description}onChange={e => setForm({...form, description: e.target.value})}/>

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

                <button onClick={() => {setEditId(c.id)
                  setForm({
                    title: c.title || "",
                    start_time: (c.start_time || "").replace("Z", "").slice(0, 16),
                    end_time: (c.end_time || "").replace("Z", "").slice(0, 16),
                    location: c.location || "",
                    description: c.description || c.raw_text || ""
                  })
                }}> Edit</button>

                <button onClick={() => reject(c.id)}>Reject</button>
              </div>
            )}
          </div>
        ))}
  
      </div>
    );
}