import {React} from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import listPlugin from '@fullcalendar/list'
import multiMonthPlugin from '@fullcalendar/multimonth'
import interactionPlugin from '@fullcalendar/interaction'
import "../CSS/Calendar.css"


const MyCalendar = ({myEvents, onDateClick, onEventClick }) => {

  return (
    <FullCalendar height="100%" expandRows={true}
        plugins={[ dayGridPlugin, timeGridPlugin, listPlugin, multiMonthPlugin, interactionPlugin ]}
        initialView="timeGridWeek"
        events={myEvents}
        dateClick={onDateClick}
        eventClick={onEventClick}
        dayMaxEvents={true}
        displayEventTime={false}
        slotLabelInterval={{ hours: 2 }}
        
        views = {{
           multiMonth3:{
              type: 'multiMonth', 
              duration: {months: 3},
              titleFormat: {month: 'short', year: 'numeric'}, 
              columnHeaderFormat: {weekday:'short'},
              buttonText: "3 Months"
           },
           timeGridWeek: { dayHeaderFormat: { weekday: "short", day: "2-digit", month: "2-digit" }},
           dayGridMonth: {dayHeaderFormat: { weekday: "short" }}
        }}

        headerToolbar = {{
          left: 'prev,next' ,
          center: 'title', 
          right: 'timeGridWeek, dayGridMonth, listWeek, multiMonth3'
        }}
    />
  )
}

export default MyCalendar