import { useState, useEffect } from "react";


function App() {
  const [age, setAge] = useState("");
  const [glucose, setGlucose] = useState("");
  const [bloodPressure, setBloodPressure] = useState("");
  const [mode, setMode] = useState("average");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [risk, setRisk] = useState(null);
  const [error, setError] = useState(null);

  const isValid =
    age !== "" &&
    glucose !== "" &&
    bloodPressure !== "" &&
    Number(age) > 0 &&
    Number(glucose) > 0 &&
    Number(bloodPressure) > 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setRisk(null);

    try {
      const response = await fetch("http://localhost:5050/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          values: [
            Number(age),
            Number(glucose),
            Number(bloodPressure),
          ],
          operation: mode,
        }),
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const data = await response.json();
      const numericResult = data.result;

      let riskLevel = "Low";
      if (numericResult > 100) riskLevel = "High";
      else if (numericResult > 70) riskLevel = "Medium";

      setResult(numericResult.toFixed(2));
      setRisk(riskLevel);
    } catch (err) {
      setError("Unable to analyze data. Please ensure services are running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Healthcare Risk Analysis</h1>

      <form onSubmit={handleSubmit}>
        <label>Age</label>
        <input
          type="number"
          value={age}
          onChange={(e) => setAge(e.target.value)}
        />

        <label>Glucose Level</label>
        <input
          type="number"
          value={glucose}
          onChange={(e) => setGlucose(e.target.value)}
        />

        <label>Blood Pressure</label>
        <input
          type="number"
          value={bloodPressure}
          onChange={(e) => setBloodPressure(e.target.value)}
        />

        <label>Computation Type</label>
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="average">Average</option>
          <option value="sum">Sum</option>
        </select>

        <button type="submit" disabled={!isValid || loading}>
          {loading ? "Processing encrypted data..." : "Analyze Risk"}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: "20px" }}>
          <p style={{ fontWeight: "bold" }}>
            Result: {result}
          </p>
          <p>
            <strong>Risk Level:</strong> {risk}
          </p>
        </div>
      )}

      {error && (
        <div style={{ marginTop: "20px", color: "red" }}>
          {error}
        </div>
      )}
    </div>
  );
}

export default App;
