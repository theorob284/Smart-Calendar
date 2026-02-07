import React, { useState, useEffect } from 'react'
import AxiosInstance from '../Calendar/AxiosInstance'
import {useParams} from "react-router-dom"
import { useNavigate } from 'react-router-dom'

export default function CheckExtractedEvent() {

    const navigate = useNavigate();
    const [checkevent, setCheckEvent] = useState([])
    const {docID} = useParams();
    const [editId, setEditId] = useState(null)
    const [form, setForm] = useState({
      title: "",
      start_time: "",
      end_time: "",
      location: "",
      description: ""
    })

    const GetData = () => {AxiosInstance.get(`/api/candidates/?document=${docID}&status=PENDING`).then((res) => { setCheckEvent(res.data);});}

    useEffect(() => {GetData();}, [docID]);

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

    return (
      <div>
        <h1>Check Event</h1>

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