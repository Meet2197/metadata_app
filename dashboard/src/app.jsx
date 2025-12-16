import { useEffect, useState } from "react";

function App() {
  const [experiments, setExperiments] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/experiments", {
      headers: {
        Authorization: "Bearer YOUR_ADMIN_TOKEN"
      }
    })
      .then(res => res.json())
      .then(data => setExperiments(data));
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>RTG Microscopy Dashboard</h1>
      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>Date</th>
            <th>User</th>
            <th>Microscope</th>
            <th>Objective</th>
            <th>Channels</th>
            <th>ELN</th>
          </tr>
        </thead>
        <tbody>
          {experiments.map(exp => (
            <tr key={exp.id}>
              <td>{exp.acquisition_date}</td>
              <td>{exp.user_id}</td>
              <td>{exp.microscope}</td>
              <td>{exp.objective}</td>
              <td>{exp.channels.join(", ")}</td>
              <td>{exp.eln_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
