
import React from 'react';
import '../CSS/Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <a href="/" className="logo">Smart Calendar</a>
      </div>
      <div className="navbar-center">
        <ul className="nav-links">
          <li><a href="/">Import Calendars</a></li>
          <li><a href="/">Create Event</a></li>
          <li><a href="/">Blank</a></li>
        </ul>
      </div>
      <div className="navbar-right">
        <a href="/" className="nav-links">
          <li><a href="/">Sign In</a></li>
        </a>
      </div>
    </nav>
  );
};

export default Navbar;