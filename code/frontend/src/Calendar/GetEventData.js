import {React, useEffect, useState} from 'react'
import MyCalendar from './DisplayCalendar'
import AxiosInstance from './AxiosInstance'
import EventModal from './CreateEvent'
import "../CSS/Calendar.css"


const Calendar = () => {

  const [events, setEvents] = useState([]);  // store all events from backend
  const [modalOpen, setModalOpen] = useState(false) //open modal
  const [selectedEvent, setSelectedEvent] = useState(null)  //store current event

  //get data from API
  const GetData = () => {AxiosInstance.get("api/events/").then((res) => setEvents(res.data))}

  useEffect(() => { GetData() }, []);

  //creaate new event
  const handleDateClick = (info) => {
    setSelectedEvent(null);
    setSelectedEvent({
      title: "",
      start_time: info.dateStr + "T09:00",
      end_time: info.dateStr + "T10:00",
      location: "",
      description: "",
      event_type: "",
    });
    setModalOpen(true);
  }

  //edit event
  const handleEventClick = (info) => {
    setSelectedEvent({
      id: info.event.id,
      title: info.event.title,
      start_time: info.event.startStr,
      end_time: info.event.endStr,
      description: info.event.extendedProps.description,
      location: info.event.extendedProps.location,
      event_type: info.event.extendedProps.event_type,
    });
    setModalOpen(true);
  };

  //save event
  const handleSave = (data) => {

    const formattedData = {...data, start_time: data.start_time + ":00", end_time: data.end_time + ":00",};

    if (selectedEvent?.id) { //update event
      AxiosInstance.put(`api/events/${selectedEvent.id}/`, formattedData).then(() => {GetData(); setModalOpen(false)});
    } else {  // create new event
      AxiosInstance.post("api/events/", formattedData).then(() => {GetData(); setModalOpen(false)});
    };
  };
 // delete event
  const handleDelete = () => {
    AxiosInstance.delete(`api/events/${selectedEvent.id}/`).then(() => {GetData(); setModalOpen(false)});
  };

  return (
    <div className="page">
      <div className="calendarWrap">
      <MyCalendar myEvents={events} onDateClick={handleDateClick} onEventClick={handleEventClick}/> 
      </div>
      <EventModal isOpen={modalOpen} onClose={() => setModalOpen(false)} onSave={handleSave} onDelete={handleDelete} selectedEvent={selectedEvent} />
    </div>
  )
}

export default Calendar