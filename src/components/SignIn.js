import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../App.css";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

function SignIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API}/signin`, { email, password });
      const { user_id } = res.data;
      localStorage.setItem("user_id", user_id);
      localStorage.setItem("user_email", email);
      alert("Login Successful!");
      navigate("/dashboard");
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Invalid credentials!");
    }
  };

  return (
    <div className="auth-container">
      <h2>Welcome Back 👋</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Enter Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Enter Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Sign In</button>
      </form>
      <p>
        Don’t have an account? <Link to="/signup">Create one</Link>
      </p>
    </div>
  );
}

export default SignIn;
