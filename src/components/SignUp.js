import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../App.css";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

function SignUp() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const navigate = useNavigate();

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API}/signup`, { email, password, name });
      const { user_id } = res.data;
      localStorage.setItem("user_id", user_id);
      localStorage.setItem("user_email", email);
      alert("Account Created Successfully!");
      navigate("/");
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Error creating account");
    }
  };

  return (
    <div className="auth-container">
      <h2>Create Account 🚀</h2>
      <form onSubmit={handleSignUp}>
        <input
          type="text"
          placeholder="Full Name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="email"
          placeholder="Enter Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Create Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Sign Up</button>
      </form>
      <p>
        Already registered? <Link to="/">Login</Link>
      </p>
    </div>
  );
}

export default SignUp;
