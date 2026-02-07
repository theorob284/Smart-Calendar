import React, { useState, useEffect } from 'react'
import AxiosInstance from '../Calendar/AxiosInstance'
import {useParams} from "react-router-dom"

export default function CheckExtractedEvent() {

    const [checkevent, setCheckEvent] = useState([])
    const {docID} = useParams();

    const GetData = () => {AxiosInstance.get(`/api/candidates?document=${docID}&status=PENDING`).then((res) => { setCheckEvent(res.data);});}

    useEffect(() => {GetData();}, [docID]);

    return (
    <div>
      <h1>Check Event</h1>

      {checkevent.map(c => (
        <div key={c.id}>
          <p>{c.title}</p>
          <p>{c.start_time}</p>
          <p>{c.end_time}</p>
          <p>{c.location}</p>
          <p>{c.raw_text}</p>
        </div>
      ))}
    </div>
  );
}