import {React, useEffect, useState} from 'react'
import MyCalendar from './DisplayCalendar'
import AxiosInstance from './AxiosInstance'
import Upload from '../FileIngestion/FileUpload'

const Calendar = () => {

  const [events, setEvents] = useState()
  const handleFileSelected = (file) => {
    console.log("Selected file:", file.name, file.type, file.size);
    //post to abckend here
  }

  const GetData = () => {
    AxiosInstance.get(`api/events/`).then((res) => 
      {setEvents(res.data)
      console.log(res.data)
    })
  }

  useEffect(() =>{GetData();},[] )

  return (
    <div> 
      <Upload onFileSelected={handleFileSelected} />
      <MyCalendar myEvents={events}/>
    </div>)
}

export default Calendar
