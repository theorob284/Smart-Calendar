import {React, useEffect, useState} from 'react'
import MyCalendar from './MyCalendar'
import AxiosInstance from './AxiosInstance'

const Calendar = () => {

  const [events, setEvents] = useState()

  const GetData = () => {
    AxiosInstance.get(`api/events/`).then((res) =>{
      setEvents(res.data)
      console.log(res.data)
    })

  }

  useEffect(() =>{GetData();},[] )

  return (
    <div>
       <MyCalendar myEvents={events}/>
    </div>
  )
}

export default Calendar
