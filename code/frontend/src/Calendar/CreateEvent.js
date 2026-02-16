import React, { useState, useEffect } from "react";

const EventModal = ({ isOpen, onClose, onSave, onDelete, selectedEvent }) => {

  const [formData, setFormData] = useState({
    title: "",
    start_time: "",
    end_time: "",
    location: "",
    event_type: "",
  });

  useEffect(() => {
    if (selectedEvent) {
      const formatDate = (dateString) => {
        if (!dateString) return "";
        return dateString.replace("Z", "").slice(0,16);
      };

      setFormData({
        title: selectedEvent.title || "",
        start_time: formatDate(selectedEvent.start_time),
        end_time: formatDate(selectedEvent.end_time),
        location: selectedEvent.location || "",
        event_type: selectedEvent.event_type || "",
      });
  }}, [selectedEvent]);

  if (!isOpen) return null;

  const handleChange = (e) => {setFormData({ ...formData, [e.target.name]: e.target.value });};
  const handleSubmit = () => {onSave(formData);};

  return (
    <div style={{ position: "fixed",top: 0, left: 0, width: "100vw", height: "100vh", backgroundColor: "rgba(0,0,0,0.5)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 1000}}>
      <div style={{background: "white", padding: "20px", borderRadius: "8px", width: "400px"}}>
        <h3>{selectedEvent?.id ? "Edit Event" : "Create Event"}</h3>

        <input name="title" placeholder="Title" value={formData.title} onChange={handleChange}/>
        <input type="datetime-local" name="start_time" value={formData.start_time} onChange={handleChange}/>
        <input type="datetime-local" name="end_time" value={formData.end_time} onChange={handleChange} />
        <input name="location" placeholder="Location"value={formData.location} onChange={handleChange} />
        <input name="event_type" placeholder="Type" value={formData.event_type} onChange={handleChange}/>

        <div style={{ marginTop: "10px" }}>
          <button onClick={handleSubmit}>Save</button>
          {selectedEvent?.id && ( <button onClick={onDelete} style={{ color: "red", marginLeft: "10px" }} > Delete</button>)}
          <button onClick={onClose} style={{ marginLeft: "10px" }} > Cancel </button>
        </div>
      </div>
    </div>
  );

};

export default EventModal;
