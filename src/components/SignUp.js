import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../App.css";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

function SignUp() {
  const [username, setUsername] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [gender, setGender] = useState("");
  const [status, setStatus] = useState("");
  const [semester, setSemester] = useState("");
  const [degreeProgram, setDegreeProgram] = useState("");
  const [degreeName, setDegreeName] = useState("");
  const [department, setDepartment] = useState("");
  const [cgpa, setCgpa] = useState("");
  const [skills, setSkills] = useState("");

  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API}/signup`, {
        username,
        firstName,
        lastName,
        email,
        gender,
        status,
        semester,
        degreeProgram,
        degreeName,
        department,
        cgpa,
        skills,
        password,
      });
      const { user_id } = res.data;
      localStorage.setItem("user_id", user_id);
      localStorage.setItem("user_email", email);
      alert("Account Created Successfully!");
      navigate("/"); // or "/dashboard"
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
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="First Name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Last Name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <select value={gender} onChange={(e) => setGender(e.target.value)} required>
          <option value="">Select Gender</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
        </select>
        <input
          type="text"
          placeholder="Status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          required
        />
        <input
          type="number"
          placeholder="Semester"
          value={semester}
          onChange={(e) => setSemester(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Degree Program"
          value={degreeProgram}
          onChange={(e) => setDegreeProgram(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Degree Name"
          value={degreeName}
          onChange={(e) => setDegreeName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Department"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          required
        />
        <input
          type="number"
          step="0.01"
          placeholder="CGPA"
          value={cgpa}
          onChange={(e) => setCgpa(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Skills (comma separated)"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
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
