import React from "react";
import { Routes, Route } from "react-router-dom";

import Calendar from "./Calendar/GetEventData";
import CheckExtractedEvent from "./ReviewExtractedEvents/CheckEvent";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Calendar />} />
      <Route path="/review/:docID" element={<CheckExtractedEvent />} />
      <Route path="/edit/:docID" element={<CheckExtractedEvent />} />
    </Routes>
  );
}
