import {React, useEffect, useState} from 'react'
import MyCalendar from './DisplayCalendar'
import AxiosInstance from './AxiosInstance'
import Upload from '../FileIngestion/FileUpload'

const Calendar = () => {

  const [events, setEvents] = useState([]);
  const GetData = () => {
    AxiosInstance.get("api/events/").then((res) => { setEvents(res.data); });
  }

   useEffect(() => {GetData();}, []);

  return (
    <div> 
      <MyCalendar myEvents={events}/>
    </div>)
}

export default Calendar
