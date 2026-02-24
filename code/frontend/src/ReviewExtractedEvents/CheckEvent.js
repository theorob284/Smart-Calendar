import React, { useState, useEffect, useCallback } from "react";
import AxiosInstance from "../Calendar/AxiosInstance";
import { useParams, useNavigate } from "react-router-dom";
import SmartPlanPanel from "../SmartLogic/SmartUI";
import Modal from "../Components/Modal";
import "../CSS/Modal.css"
import "../CSS/checkEvent.css"
import "../CSS/EventModal.css"


// check event duration (min: 5 minutes)
function isValidDuration(start, end, mins = 5) {
  if (!start || !end) return false;
  const startDate = new Date(start);
  const endDate = new Date(end);
  if (isNaN(startDate) || isNaN(endDate)) return false;

  return endDate - startDate >= mins * 60000;
}

export default function CheckExtractedEvent() {
  const navigate = useNavigate();
  const { docID } = useParams();

  const [checkevent, setCheckEvent] = useState([]); // store pending candidates
  const [createdevents, setCreatedEvents] = useState([]);  // store created events
  const [conflictbyid, setConflictById] = useState({});  // store no. of conflicts

  // accept/reject loading states
  const [accepting, setAccepting] = useState(false);
  const [counter, setCounter] = useState(0);

  const [rejecting, setRejecting] = useState(false);
  const [counterRej, setRejCounter] = useState(0);

  //editing states
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({
    title: "",
    start_time: "",
    end_time: "",
    location: "",
    event_type: "",
    description: "",
  });
  const [openModal, setOpenModal] = useState(false);

  const isInvalidDuration = !isValidDuration(form.start_time,form.end_time,5);

  // fetch pending candidates
  const GetData = useCallback(() => {AxiosInstance.get(`/api/candidates/?document=${docID}&status=PENDING`).then((res) => {setCheckEvent(res.data);});}, [docID]);
  useEffect(() => {GetData();}, [GetData]);

  // fetch existing events
  useEffect(() => {AxiosInstance.get(`/api/events/`).then((res) => {setCreatedEvents(res.data);});}, []);

  // calculate conflicts
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

      // check for conflicts with events
      for (const events of createdevents) {
        if (!events.start_time || !events.end_time) continue;
        const eventStart = new Date(events.start_time).getTime();
        const eventEnd = new Date(events.end_time).getTime();

        const conflict = pendingStart < eventEnd && pendingEnd > eventStart;

        if (conflict) conflictCounter += 1;
      }

      // check for conflicts with candidates
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

  const updateStatus = (id) => { // remove candidate after accept/reject
    setCheckEvent((prev) => {
      const updated = prev.filter((c) => c.id !== id);
      if (updated.length === 0) {
        navigate("/");
      }
      return updated;
    });
  };

  // accept one candidate
  const accept = async (id) => {
    await AxiosInstance.post(`/api/candidates/${id}/accept/`);
    updateStatus(id);
  };

  // reject one candidate
  const reject = async (id) => {
    await AxiosInstance.post(`/api/candidates/${id}/reject/`);
    updateStatus(id);
  };

  // accept all candidates
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

  //reject all candidates
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

  const edit = async (id) => { //edit candidates details
    await AxiosInstance.patch(`/api/candidates/${id}/`, {
      title: form.title,
      start_time: form.start_time,
      end_time: form.end_time,
      location: form.location,
      event_type: form.event_type,
      description: form.description,
    });

    GetData();
    setEditId(null);
  };

  const handleSmartApplied = async () => {
  // refresh candidates
  const res = await AxiosInstance.get(`/api/candidates/?document=${docID}&status=PENDING`);

  const remaining = res.data;
  setCheckEvent(remaining);

  // refresh events
  const eventRes = await AxiosInstance.get("/api/events/");
  setCreatedEvents(eventRes.data);

  // navigate only if nothing left
  if (remaining.length === 0) {
    navigate("/");
  }
};

  return (
    <div className="checkPage">
      <div className="checkHeader">
        <div>
          <h1>Check Events</h1>
          <p className="checkSub">Review extracted items before adding them to your calendar.</p>
        </div>

        <div className="checkActions">
          <button className="btnPrimary" onClick={AcceptAll} disabled={accepting}> Accept all</button>
          <button className="btnDanger" onClick={RejectAll} disabled={rejecting}> Reject all</button>
          <button className="btnGhost" onClick={() => setOpenModal(true)}>Smart Plan</button>
        </div>
     </div>
      {accepting && <p className="checkStatus">Processing {counter} of {checkevent.length}</p>}
      {rejecting && <p className="checkStatus">Processing {counterRej} of {checkevent.length}</p>}

      <Modal open={openModal} title="Smart Plan Preferences"onClose={() => setOpenModal(false)} >
        <SmartPlanPanel docID={docID} onApplied={async () => { await handleSmartApplied(); setOpenModal(false);}}/>
      </Modal>

      <div className="checkList">
        {checkevent.map((c) => {
          const startLabel = c.start_time ? new Date(c.start_time).toLocaleString() : "No start time";
          const endLabel = c.end_time ? new Date(c.end_time).toLocaleString() : "No end time";

          return (
            <div key={c.id} className="checkCard">
              {editId === c.id ? (<>
                  
                  <div className="field">
                    <label>Title</label>
                    <input value={form.title} maxLength={150} onChange={(e) => setForm({ ...form, title: e.target.value })}/>
                  </div>
                  <div className="editGrid">
                    <div className="editField">
                      <label>Start</label>
                      <input type="datetime-local" value={form.start_time}  onChange={(e) => setForm({ ...form, start_time: e.target.value })}/>
                    </div>
                    <div className="editField">
                      <label>End</label>
                      <input type="datetime-local" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} />
                    </div>
                    <div className="editField">
                      <label>Location</label>
                      <input value={form.location} maxLength={150} onChange={(e) => setForm({ ...form, location: e.target.value })}/>
                    </div>
                    <div className="editField">
                      <label>Type</label>
                      <input value={form.event_type} maxLength={150} onChange={(e) => setForm({ ...form, event_type: e.target.value })}/>
                    </div>
                    <div className="editField fullWidth">
                      <label>Description</label>
                      <input value={form.description} maxLength={400} onChange={(e) => setForm({ ...form, description: e.target.value })}/>
                    </div>
                  </div>

                  {isInvalidDuration && (<p className="errorText">End time must be at least 5 minutes after start time.</p>)}
                  <div className="checkCardActions">
                    <button className="btnPrimary" onClick={() => edit(c.id)}  disabled={isInvalidDuration} >Save</button>
                    <button className="btnGhost" onClick={() => setEditId(null)}>Cancel</button>
                  </div>
                </>
              ) : (<>
                  <div className="checkCardTop">
                    <div>
                      <div className="checkTitle">{c.title || "Untitled event"}</div>
                      <div className="checkMeta">
                        <span>{startLabel}</span>
                        <span>→</span>
                        <span>{endLabel}</span>
                      </div>
                      {c.location && <div className="checkMeta">{c.location}</div>}
                    </div>
                    <div className="checkBadge">Conflicts: {conflictbyid[c.id] ?? 0}</div>
                  </div>

                  <div className="checkCardActions">
                    <button className="btnPrimary" onClick={() => accept(c.id)}> Accept</button>
                    <button className="btnGhost"
                      onClick={() => {
                        setEditId(c.id);
                        setForm({
                          title: c.title || "",
                          start_time: (c.start_time || "").replace("Z", "").slice(0, 16),
                          end_time: (c.end_time || "").replace("Z", "").slice(0, 16),
                          location: c.location || "",
                          event_type: c.event_type || "",
                          description: c.description || "",
                        });
                      }}> Edit</button>

                    <button className="btnDanger" onClick={() => reject(c.id)}> Reject</button>
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}