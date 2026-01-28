import './App.css';
import FullCalendar from '@fullcalendar/react'
import dayGrid from '@fullcalendar/daygrid'

function Calendar() {
  //const Calendar=()=>{<FullCalendar/>}
  return (
    <FullCalendar
      plugins={[ dayGrid ]}
      initialView="dayGridMonth"
    />
  );
}

export default Calendar;
