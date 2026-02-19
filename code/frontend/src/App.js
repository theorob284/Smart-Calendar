import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import Navbar from "./Components/NavBar";

import Calendar from "./Calendar/GetEventData";
import CheckExtractedEvent from "./ReviewExtractedEvents/CheckEvent";
import Upload from "./FileIngestion/FileUpload";
import Login from "./Components/Login";
import Register from "./Components/Register";
import RequireAuth from "./Components/RequireAuth";

export default function App() {
  const location = useLocation();
  const hideNavbar = ["/login", "/register"].includes(location.pathname);

  return (<>
      {!hideNavbar && <Navbar />}

      <Routes>
        <Route path="/" element={<Calendar />} />
        <Route path="/review/:docID" element={<CheckExtractedEvent />} />
        <Route path="/edit/:docID" element={<CheckExtractedEvent />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </>
  );
}
