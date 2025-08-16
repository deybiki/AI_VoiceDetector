import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Hero from "../Hero";

const ViewTest = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const username = localStorage.getItem("username");

  console.log("profname:", username);
  useEffect(() => {
    const fetchTests = async () => {
      try {
        const res = await axios.get(
          "http://localhost:5000/api/examiner/get-tests",
          { withCredentials: true }
        );
        setTests(res.data.tests || []);
      } catch (err) {
        toast.error("Failed to fetch tests");
      } finally {
        setLoading(false);
      }
    };
    fetchTests();
  }, []);

  if (loading)
    return (
      <div className="text-center mt-5">
        <div className="spinner-border text-primary" role="status"></div>
        <div>Loading tests...</div>
      </div>
    );

  return (
    <>
      <Hero />
      <div className="container py-4">
        <ToastContainer />
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2
  style={{
    fontSize: "2.2rem",
    fontWeight: "600",
    color: "#000000",
    letterSpacing: "1px",
    fontFamily: "'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    marginBottom: "1rem"
  }}
>
  Created Tests
</h2>


          <button
            className="btn btn-primary"
            onClick={() => navigate(`/prof-dash/${username}`)}
          >
            Back to Dashboard
          </button>
        </div>
        {tests.length === 0 ? (
          <div
            className="text-center py-4 px-3 rounded shadow"
            style={{ backgroundColor: "#e6f2ff" }}
          >
            <img
              src="https://cdn-icons-png.flaticon.com/512/4076/4076503.png"
              alt="No Tests"
              style={{ maxWidth: "90px", marginBottom: "12px" }}
            />
            <div className="text-primary fw-semibold mt-2">No tests found.</div>
          </div>
        ) : (
          <div className="row g-4 mt-3">
  {tests.map((test) => (
    <div className="col-md-6 col-lg-4" key={test._id}>
      <div
        className="card h-100 shadow-lg border-0"
        style={{
          background: "#e6f4ff",
          borderRadius: "18px",
          transition: "transform 0.3s ease",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.02)")}
        onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
      >
        <div className="card-body d-flex flex-column">
          <h5
            className="card-title fw-semibold mb-3"
            style={{ color: "#0d6efd", fontSize: "1.4rem" }}
          >
            {test.title}
          </h5>

          <ul
            className="list-unstyled mb-4"
            style={{ fontSize: "1.05rem", lineHeight: "1.6" }}
          >
            <li>
              <strong>Department:</strong> {test.department || "N/A"}
            </li>
            <li>
              <strong>Start:</strong>{" "}
              {new Date(test.start_time).toLocaleString("en-IN", {
                timeZone: "Asia/Kolkata",
              })}
            </li>
            <li>
              <strong>End:</strong>{" "}
              {new Date(test.end_time).toLocaleString("en-IN", {
                timeZone: "Asia/Kolkata",
              })}
            </li>
            <li>
              <strong>No. of Questions:</strong>{" "}
              {test.questions ? test.questions.length : 0}
            </li>
            <li>
              <strong>No. of Students:</strong>{" "}
              {test.students ? test.students.length : 0}
            </li>
          </ul>

          <div className="mt-auto text-end">
            <button
              className="btn btn-sm px-4 py-2"
              style={{
                backgroundColor: "#0d6efd",
                color: "white",
                border: "none",
                borderRadius: "8px",
                fontSize: "1rem",
              }}
              onClick={() =>
                navigate(`/prof-dash/${username}/test/${test._id}`)
              }
            >
              View Details
            </button>
          </div>
        </div>
      </div>
    </div>
  ))}
</div>

        )}
      </div>
    </>
  );
};

export default ViewTest;
