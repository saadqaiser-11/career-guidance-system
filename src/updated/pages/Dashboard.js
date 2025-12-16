import React from "react";
import { useNavigate } from "react-router-dom";
import QuizFlow from "../components/QuizFlow";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");
    navigate("/");
  };

  return (
    <div className="dashboard-wrapper">
      <button className="logout-btn" onClick={handleLogout}>
        Logout
      </button>
      <div className="dashboard-header">
        <h1>Career Guidance Dashboard</h1>
        <p>Take a quiz to discover your career path</p>
      </div>
      <QuizFlow />
    </div>
  );
}

export default Dashboard;