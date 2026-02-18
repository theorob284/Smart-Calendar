import React, { useState, useEffect } from "react";
import "../CSS/EventModal.css"
import Modal from "../Components/Modal";

const EventModal = ({ isOpen, onClose, onSave, onDelete, selectedEvent }) => {

  const [formData, setFormData] = useState({
    title: "",
    start_time: "",
    end_time: "",
    location: "",
    event_type: "",
    description: "",
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
        description: selectedEvent.description || "",
      });
  }}, [selectedEvent]);

  if (!isOpen) return null;

  const handleChange = (e) => {setFormData({ ...formData, [e.target.name]: e.target.value });};
  const handleSubmit = () => {onSave(formData);};

  return (
    <Modal open={isOpen} title={selectedEvent?.id ? "Edit Event" : "Create Event"} onClose={onClose}>
      <div>
        <label className="field">
          <span>Title</span>
          <input name="title" maxLength={150} value={formData.title} onChange={handleChange}/>
        </label>

        <div className="grid2">
          <label className="field">
            <span>Start</span>
            <input type="datetime-local" name="start_time" value={formData.start_time} onChange={handleChange}/>
          </label>

          <label className="field">
            <span>End</span>
            <input type="datetime-local" name="end_time" value={formData.end_time} onChange={handleChange}/>
          </label>
        </div>

        <div className="grid2">
          <label className="field">
            <span>Location</span>
            <input name="location" maxLength={150} value={formData.location} onChange={handleChange}/>
          </label>

          <label className="field">
            <span>Type</span>
            <input name="event_type" maxLength={30} value={formData.event_type} onChange={handleChange}/>
          </label>
        </div>

        <label className="field">
            <span>Description</span>
            <input name="description" maxLength={400} value={formData.description} onChange={handleChange}/>
        </label>

        <div className="modalFooter">
          <button className="btnPrimary" onClick={handleSubmit}> Save</button>
          {selectedEvent?.id && ( <button className="btnDanger" onClick={onDelete}> Delete</button>)}
          <button className="btnGhost" onClick={onClose}> Cancel</button>
        </div>
      </div>
    </Modal>
  );
}
export default EventModal;
