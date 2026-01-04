import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminDashboard.css";

export default function AdminDashboard() {
  const [data, setData] = useState([]);
  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const res = await fetch(
        "https://backendofcareer-production.up.railway.app/api/admin/results?username=admin@gmail.com&password=admin123"
      );
      const json = await res.json();
      setData(json);
    } catch (error) {
      console.error("Error loading data:", error);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const AGENT_URL = "https://imani-littlish-mckenna.ngrok-free.dev/chatbox";

  const induct = async (id) => {
    try {
      // 1️⃣ First, induct the student in the backend
      await fetch(
        `https://backendofcareer-production.up.railway.app/api/admin/induct/${id}?username=admin@gmail.com&password=admin123`,
        { method: "POST" }
      );

      // 2️⃣ Find the student data for the agent prompt
      const student = data.find((d) => d.id === id);

      // 3️⃣ Call the agent (fire and forget - no await)
      if (student) {
        const agentPrompt = `You are an assistant that MUST call tools.
RULES:
- Do NOT ask follow-up questions
- Do NOT explain anything
- ALWAYS call the update_student tool

TASK:
Update an existing student record.

STUDENT IDENTIFIER:
Email: ${student.email || "N/A"}

UPDATED DATA:
- inducted: true
- student_name: ${student.student_name || "N/A"}
- score: ${student.score}
- fit: ${student.fit}`;

        // Fire and forget - don't wait for response
        fetch(AGENT_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: agentPrompt,
            thread_id: `update-student-${id}`,
          }),
        }).catch((err) => console.warn("⚠️ Agent call failed:", err));
      }

      loadData();
    } catch (error) {
      console.error("Error inducting student:", error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");
    navigate("/");
  };

  return (
    <div className="admin-dashboard">
      <button className="logout-btn" onClick={handleLogout}>
        Logout
      </button>
      
      <div className="admin-header">
        <h2>Admin Dashboard</h2>
        <p>Review and manage student quiz results</p>
      </div>

      <div className="admin-table-container">
        {data.length === 0 ? (
          <div className="empty-state">No results available yet</div>
        ) : (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Score</th>
                <th>Fit Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {data.map((d) => (
                <tr key={d.id}>
                  <td>{d.student_name || "N/A"}</td>
                  <td>
                    {d.score}/{d.max_score}
                  </td>
                  <td>
                    <span className={`fit-badge ${d.fit ? "fit" : "not-fit"}`}>
                      {d.fit ? "✓ Fit" : "✗ Not Fit"}
                    </span>
                  </td>
                  <td>
                    <button
                      className={`induct-btn ${d.inducted ? "inducted" : ""}`}
                      disabled={!d.fit || d.inducted}
                      onClick={() => induct(d.id)}
                    >
                      {d.inducted ? "✓ Inducted" : "Induct"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
