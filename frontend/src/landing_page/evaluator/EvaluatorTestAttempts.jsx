import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";

export default function EvaluatorPage() {
  const [results, setResults] = useState([]);
  const [feedback, setFeedback] = useState({});
  const [remarks, setRemarks] = useState({});
  const [submitted, setSubmitted] = useState({}); // ✅ track submissions

  const { testId } = useParams();
  console.log("testId:", testId);

  useEffect(() => {
    if (testId) {
      axios
        .get(`http://localhost:5000/api/evaluator/${testId}/results`)
        .then((res) => {
          console.log("📌 Viva Results:", res.data);
          setResults(res.data);
        })
        .catch((err) => console.error(err));
    }
  }, [testId]);

  // ⭐ star rating setter
  const handleStarClick = (studentId, rating) => {
    setFeedback({ ...feedback, [studentId]: rating });
  };

  const handleSubmit = async (studentId) => {
    try {
      const starValue = feedback[studentId] || 0;
      const score = starValue * 2; // ⭐ convert stars to marks

      const payload = {
        testId,
        candidateId: studentId,
        score,
        remarks: remarks[studentId] || "",
      };

      console.log("📤 Payload being sent:", payload);

      await axios.post(
        `http://localhost:5000/api/evaluator/resultsubmit`,
        payload
      );

      alert("Feedback submitted!");

      // ✅ mark this student as submitted
      setSubmitted((prev) => ({ ...prev, [studentId]: true }));
    } catch (error) {
      console.error("❌ Error submitting feedback:", error);
    }
  };

  return (
    <div className="container my-4">
      <h2 className="text-center mb-4">Evaluator Page</h2>

      {results.length === 0 ? (
        <p className="text-center text-muted">No tests to evaluate</p>
      ) : (
        results.map((viva) => (
          <div key={viva._id} className="card shadow-sm mb-4">
            <div className="card-body">
              <h5 className="card-title">Student: {viva.candidateId}</h5>
              {/* <p className="card-text">
                <b>Total Score:</b> {viva.totalScore}
              </p> */}

              {viva.questionAnswerPairs.map((qa, idx) => (
                <div key={qa._id} className="mb-2">
                  <p className="mb-1">
                    <b>Q{idx + 1}:</b> {qa.question}
                  </p>
                  <p className="text-muted">
                    <b>Answer:</b> {qa.answer}
                  </p>
                </div>
              ))}

              {/* ⭐ Star Rating */}
              <div className="mb-3">
                <label className="form-label fw-bold">Feedback (Stars):</label>
                <div>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <span
                      key={star}
                      onClick={() => handleStarClick(viva.candidateId, star)}
                      style={{
                        fontSize: "1.5rem",
                        cursor: "pointer",
                        color:
                          star <= (feedback[viva.candidateId] || 0)
                            ? "gold"
                            : "lightgray",
                      }}
                    >
                      ★
                    </span>
                  ))}
                </div>
              </div>

              {/* Remarks textarea */}
              <div className="mb-3">
                <label className="form-label fw-bold">Remarks</label>
                <textarea
                  className="form-control"
                  placeholder="Write remarks..."
                  value={remarks[viva.candidateId] || ""}
                  onChange={(e) =>
                    setRemarks({
                      ...remarks,
                      [viva.candidateId]: e.target.value,
                    })
                  }
                  disabled={submitted[viva.candidateId]} // ✅ disable if submitted
                />
              </div>

              {/* ✅ Submit or Finished */}
              {submitted[viva.candidateId] ? (
                <span className="badge bg-success p-2">✅ Finished</span>
              ) : (
                <button
                  className="btn btn-primary"
                  onClick={() => handleSubmit(viva.candidateId)}
                >
                  Submit Feedback
                </button>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
