import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminDashboard.css";

export default function AdminDashboard() {
  const [data, setData] = useState([]);
  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const res = await fetch(
        "http://localhost:8000/api/admin/results?username=admin@gmail.com&password=admin123"
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

  const induct = async (id) => {
    try {
      await fetch(
        `http://localhost:8000/api/admin/induct/${id}?username=admin@gmail.com&password=admin123`,
        { method: "POST" }
      );
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
