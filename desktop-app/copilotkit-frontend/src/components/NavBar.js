import React from "react";
import { Link } from "react-router-dom";

function NavBar() {
  return (
    <nav className="navbar">
      <Link to="/">Dashboard</Link>
      <Link to="/missions">Missions</Link>
      <Link to="/analytics">Analytics</Link>
      <Link to="/settings">Settings</Link>
      <Link to="/agentic-generative-ui">Agentic Generative UI</Link>
    </nav>
  );
}

export default NavBar;
