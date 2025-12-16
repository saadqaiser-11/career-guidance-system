import { useEffect, useState } from "react";

export default function AdminDashboard() {
  const [data, setData] = useState([]);

  const loadData = async () => {
    const res = await fetch(
      "http://localhost:8000/api/admin/results?username=admin@gmail.com&password=admin123"
    );
    const json = await res.json();
    setData(json);
    console.log(json);
  };

  useEffect(() => {
    loadData();
  }, []);

  const induct = async (id) => {
    await fetch(
      `http://localhost:8000/api/admin/induct/${id}?username=admin@gmail.com&password=admin123`,
      { method: "POST" }
    );
    loadData();
  };

  return (
    <div>
      <h2>Admin Dashboard</h2>
      <table border="1">
        <thead>
          <tr>
            <th>Student</th>
            <th>Marks</th>
            <th>Fit</th>
            <th>Induct</th>
          </tr>
        </thead>
        <tbody>
          {data.map(d => (
            <tr key={d.id}>
              <td>{d.student_name || "N/A"}</td>
              <td>{d.score}/{d.max_score}</td>
              <td>{d.fit ? "Fit" : "Not Fit"}</td>
              <td>
                <button
                  disabled={!d.fit || d.inducted}
                  onClick={() => induct(d.id)}
                >
                  {d.inducted ? "Inducted" : "Induct"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
