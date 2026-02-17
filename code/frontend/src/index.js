import React from 'react';
import ReactDOM from 'react-dom/client';
import './CSS/index.css';
import reportWebVitals from './reportWebVitals';
import App from './App';
import { BrowserRouter } from 'react-router-dom';
import Navbar from './Components/NavBar';
import "./CSS/Buttons.css";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Navbar />
      <App/>
    </BrowserRouter>
  </React.StrictMode>
  
);

reportWebVitals();
