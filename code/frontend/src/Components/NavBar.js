
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
          <li><a href="/upload">Import Calendar</a></li>
        </ul>
      </div>
      <div className="navbar-right">
        <h5>Personalise your Calendar</h5>
      </div>
    </nav>
  );
};

export default Navbar;