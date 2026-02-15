import {React} from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import listPlugin from '@fullcalendar/list'
import multiMonthPlugin from '@fullcalendar/multimonth'
import interactionPlugin from '@fullcalendar/interaction'


const MyCalendar = ({myEvents, onDateClick, onEventClick }) => {

  return (
    <FullCalendar
        plugins={[ dayGridPlugin, timeGridPlugin, listPlugin, multiMonthPlugin, interactionPlugin ]}
        initialView="dayGridMonth"
        events={myEvents}
        dateClick={onDateClick}
        eventClick={onEventClick}

        views = {{
           multiMonth3:{
              type: 'multiMonth', 
              duration: {months: 3},
              titleFormat: {month: 'short', year: 'numeric'}, 
              columnHeaderFormat: {weekday:'short'},
              buttonText: "3 Months"
           }
        }}

        headerToolbar = {{
          left: 'prev,next' ,
          center: 'title', 
          right: 'dayGridMonth, timeGridWeek, listDay, multiMonth3'
        }}
    />
  )
}

export default MyCalendar