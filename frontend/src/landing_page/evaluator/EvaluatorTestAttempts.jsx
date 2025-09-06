import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";

export default function EvaluatorPage() {
  const [results, setResults] = useState([]);
  const [feedback, setFeedback] = useState({}); // { studentId: { qIndex: stars } }
  const [remarks, setRemarks] = useState({});   // { studentId: { qIndex: text } }
  const [submitted, setSubmitted] = useState({});

  const { testId } = useParams();

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
  const handleStarClick = (studentId, qIndex, rating) => {
    setFeedback((prev) => ({
      ...prev,
      [studentId]: { ...(prev[studentId] || {}), [qIndex]: rating },
    }));
  };

  // Remarks setter
  const handleRemarkChange = (studentId, qIndex, value) => {
    setRemarks((prev) => ({
      ...prev,
      [studentId]: { ...(prev[studentId] || {}), [qIndex]: value },
    }));
  };

  const handleSubmit = async (studentId, questions) => {
    try {
      // Build questionwise_details
      const questionwise_details = questions.map((qa, idx) => ({
        question_score: (feedback[studentId]?.[idx] || 0) * 2, // ⭐ example: stars ×2
        remarks: remarks[studentId]?.[idx] || "",
      }));

      // Compute total score
      const score = questionwise_details.reduce(
        (sum, q) => sum + q.question_score,
        0
      );

      const payload = {
  testId,
  candidateId: studentId,
  score, // cumulative score (sum of all question scores ya jo formula chahiye)
  remarks: "Overall remarks here (optional)", // agar chahiye toh
  questionwise_details, // array of { question_score, remarks }
};

console.log("📤 Payload being sent:", payload);

await axios.post(
  `http://localhost:5000/api/evaluator/resultsubmit`,
  payload
);


      alert("Feedback submitted!");
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

              {viva.questionAnswerPairs.map((qa, idx) => (
                <div key={qa._id} className="mb-3 border-bottom pb-2">
                  <p className="mb-1">
                    <b>Q{idx + 1}:</b> {qa.question}
                  </p>
                  <p className="text-muted">
                    <b>Answer:</b> {qa.answer}
                  </p>

                  {/* ⭐ Star Rating per question */}
                  <div className="mb-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <span
                        key={star}
                        onClick={() =>
                          handleStarClick(viva.candidateId, idx, star)
                        }
                        style={{
                          fontSize: "1.5rem",
                          cursor: "pointer",
                          color:
                            star <= (feedback[viva.candidateId]?.[idx] || 0)
                              ? "gold"
                              : "lightgray",
                        }}
                      >
                        ★
                      </span>
                    ))}
                  </div>

                  {/* Remarks per question */}
                  <textarea
                    className="form-control"
                    placeholder="Write remarks..."
                    value={remarks[viva.candidateId]?.[idx] || ""}
                    onChange={(e) =>
                      handleRemarkChange(viva.candidateId, idx, e.target.value)
                    }
                    disabled={submitted[viva.candidateId]}
                  />
                </div>
              ))}

              {/* ✅ Submit or Finished */}
              {submitted[viva.candidateId] ? (
                <span className="badge bg-success p-2">✅ Finished</span>
              ) : (
                <button
                  className="btn btn-primary mt-3"
                  onClick={() =>
                    handleSubmit(viva.candidateId, viva.questionAnswerPairs)
                  }
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
