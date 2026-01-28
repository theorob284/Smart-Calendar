
import FullCalendar from '@fullcalendar/react'
import dayGrid from '@fullcalendar/daygrid'

//This function handles the FullCalendar.js library 
function Calendar() {
  //const Calendar=()=>{<FullCalendar/>}
  return (
    <FullCalendar plugins={[ dayGrid ]} initialView="dayGridMonth"/>
  );
}

export default Calendar;
