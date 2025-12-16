import React, { useEffect, useState } from "react";
import axios from "axios";
import "./QuizFlow.css";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

function QuizFlow() {
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState("");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const userId = localStorage.getItem("user_id");

  useEffect(() => {
    axios.get(`${API}/categories`).then(res => setCategories(res.data.categories));
  }, []);

  const chooseCategory = async () => {
    if (!category) return alert("Select a category");
    setLoading(true);
    try {
      const res = await axios.get(`${API}/questions?category=${encodeURIComponent(category)}`);
      setQuestions(res.data.questions);
      setAnswers({});
    } catch (err) {
      alert(err.response?.data?.detail || "Error loading questions");
    } finally {
      setLoading(false);
    }
  };

  const selectOption = (qId, idx) => setAnswers(prev => ({ ...prev, [qId]: idx }));

  const submit = async () => {
    const ansArray = Object.keys(answers).map(qid => ({ question_id: qid, selected_index: answers[qid] }));
    if (ansArray.length !== questions.length) return alert("Please answer all questions.");
    const payload = { user_id: userId, category, answers: ansArray };
    setLoading(true);
    try {
      const res = await axios.post(`${API}/submit`, payload);
      setResult(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Error submitting answers");
    } finally {
      setLoading(false);
    }
  };

  if (!userId) return <div className="quiz-container">Please sign in to continue.</div>;

  if (result) {
    return (
      <div className="quiz-container">
        <div className="quiz-card">
          <h2>Result — {result.category}</h2>
          <p><strong>Score:</strong> {result.score}/{result.max_score}</p>
          <p><strong>Fit:</strong> {result.fit ? "Yes" : "Not yet"}</p>
          <div className="result-text">
            <h4>Suggestion:</h4>
            <p>{result.suggested_text}</p>
          </div>
          <button onClick={() => { setResult(null); setQuestions([]); setCategory(""); }}>
            Try Another
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="quiz-container">
      {!questions.length ? (
        <div className="quiz-card">
          <h2>Select Category</h2>
          <select value={category} onChange={e => setCategory(e.target.value)}>
            <option value="">-- choose --</option>
            {categories.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <button onClick={chooseCategory}>{loading ? "Loading..." : "Get Questions"}</button>
        </div>
      ) : (
        <div className="quiz-card">
          <h2>Category: {category}</h2>
          {questions.map((q, i) => (
            <div key={q.id} className="question-card">
              <p><strong>{i + 1}. {q.question}</strong></p>
              <div className="quiz-option">
                {q.options.map((opt, idx) => (
                  <label key={idx}>
                    <input
                      type="radio"
                      name={q.id}
                      checked={answers[q.id] === idx}
                      onChange={() => selectOption(q.id, idx)}
                    />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <div style={{ textAlign: "center" }}>
            <button onClick={submit}>{loading ? "Submitting..." : "Submit Answers"}</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default QuizFlow;
