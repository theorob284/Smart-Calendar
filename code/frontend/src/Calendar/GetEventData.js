import {React, useEffect, useState} from 'react'
import MyCalendar from './DisplayCalendar'
import AxiosInstance from './AxiosInstance'
import EventModal from './CreateEvent'

const Calendar = () => {

  const [events, setEvents] = useState([]);
  const [modalOpen, setModalOpen] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState(null)

  const GetData = () => {
    AxiosInstance.get("api/events/").then((res) => setEvents(res.data))
  }

   useEffect(() => { GetData() }, []);


  const handleDateClick = (info) => {

    setSelectedEvent(null);
    
    setSelectedEvent({
      title: "",
      start_time: info.dateStr + "T09:00",
      end_time: info.dateStr + "T10:00",
      location: "",
      event_type: "",
    });
    setModalOpen(true);
  }


  const handleEventClick = (info) => {

    setSelectedEvent({
      id: info.event.id,
      title: info.event.title,
      start_time: info.event.startStr,
      end_time: info.event.endStr,
      location: info.event.extendedProps.location,
      event_type: info.event.extendedProps.event_type,
    });

    setModalOpen(true);

  };


  const handleSave = (data) => {

    const formattedData = {
      ...data,
      start_time: data.start_time + ":00",
      end_time: data.end_time + ":00",
    };

    if (selectedEvent?.id) {
      AxiosInstance.put(`api/events/${selectedEvent.id}/`, formattedData)
        .then(() => {
          GetData()
          setModalOpen(false)
        });
    } else {
      AxiosInstance.post("api/events/", formattedData)
        .then(() => {
          GetData()
          setModalOpen(false)
        });
    };
  };

  const handleDelete = () => {
    AxiosInstance.delete(`api/events/${selectedEvent.id}/`)
      .then(() => {
        GetData()
        setModalOpen(false)
      });
  };


  return (
    <div>
      <MyCalendar
        myEvents={events}
        onDateClick={handleDateClick}
        onEventClick={handleEventClick}
      />

      <EventModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleSave}
        onDelete={handleDelete}
        selectedEvent={selectedEvent}
      />
    </div>
  )
}

export default Calendar