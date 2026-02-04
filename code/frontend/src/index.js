import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Calendar from './Calendar/GetEventData';
import reportWebVitals from './reportWebVitals';
import Upload from './FileIngestion/FileUpload';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
      
    <Calendar />
  </React.StrictMode>
  
);

reportWebVitals();
