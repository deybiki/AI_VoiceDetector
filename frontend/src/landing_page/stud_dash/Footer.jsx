import React, { useEffect, useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { motion } from "framer-motion";
import "./Footer.css";

const Footer = () => {
  const candidateId = localStorage.getItem("username") || null;
  const studentId = localStorage.getItem("username");

  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [startingTestId, setStartingTestId] = useState(null);

  const [vivaResults, setVivaResults] = useState([]);
  const [loadingViva, setLoadingViva] = useState(true);

  // { [testId]: "title" }
  const [testTitles, setTestTitles] = useState({});

  // ---------------- Fetch Upcoming Tests ----------------
  useEffect(() => {
    const fetchTests = async () => {
      try {
        console.log("📡 GET /api/student/upcoming");
        const res = await axios.get(
          "http://localhost:5000/api/student/upcoming",
          {
            withCredentials: true,
          }
        );
        setTests(res.data?.tests || []);
      } catch (err) {
        console.error(
          "❌ upcoming tests error:",
          err.response?.data || err.message
        );
      } finally {
        setLoading(false);
      }
    };
    fetchTests();
  }, []);

  // ---------------- Fetch Viva Results ----------------
  useEffect(() => {
    const fetchVivaResults = async () => {
      try {
        if (!candidateId) {
          console.warn("⚠️ candidateId missing, skipping viva fetch");
          setLoadingViva(false);
          return;
        }

        console.log(`📡 GET /api/evaluator/${candidateId}/studresults`);
        const res = await axios.get(
          `http://localhost:5000/api/evaluator/${candidateId}/studresults`,
          { withCredentials: true }
        );
        console.log(
          "listings received from viva for particular schid",
          res.data
        );
        // ✅ sirf wahi results lo jinke pass testId ho
        const docs = Array.isArray(res.data)
          ? res.data.filter((d) => d?.testId)
          : [];

        console.log("docs (with only valid testId):", docs);
        setVivaResults(docs);

        // 🔑 Each result's `_id` == Test._id → fetch titles
        const ids = [...new Set(docs.map((d) => d?.testId).filter(Boolean))];
        console.log("🧾 testIds from viva:", ids);

        ids.forEach((id) => {
          if (!testTitles[id]) fetchTestTitle(id);
        });
      } catch (err) {
        console.error(
          "❌ viva results error:",
          err.response?.data || err.message
        );
      } finally {
        setLoadingViva(false);
      }
    };

    fetchVivaResults();
  }, [candidateId]); // run when candidateId available

  // ---------------- Fetch Test Title by Test _id ----------------
  const fetchTestTitle = async (sharedLinkId) => {
    try {
      console.log(`📡 GET /api/test/${sharedLinkId}/title`);
      const res = await axios.get(
        `http://localhost:5000/api/test/${sharedLinkId}/title`,
        {
          withCredentials: true,
        }
      );
      setTestTitles((prev) => ({
        ...prev,
        [sharedLinkId]: res.data?.title || "Untitled Test",
      }));
    } catch (err) {
      console.error(
        `❌ title fetch error (${sharedLinkId}):`,
        err.response?.data || err.message
      );
      setTestTitles((prev) => ({ ...prev, [sharedLinkId]: "Title not found" }));
    }
  };

  // ---------------- Start Test ----------------
  const handleStartTest = async (test) => {
    const testMongoId = test._id;
    const sharedLinkId = test.sharedLinkId;

    setStartingTestId(testMongoId);
    try {
      await axios.post(
        `http://localhost:5000/api/student/join/${testMongoId}`,
        {},
        { withCredentials: true }
      );

      const res = await axios.post(
        `http://localhost:5000/api/student/start/${testMongoId}`,
        {},
        { withCredentials: true }
      );

      if (res.status === 200) {
        const streamlitUrl = `http://localhost:8501/?testId=${sharedLinkId}&studentId=${studentId}`;
        window.open(streamlitUrl, "_blank");
      } else {
        alert(
          "⚠️ Could not start the test. Server returned unexpected response."
        );
      }
    } catch (err) {
      console.error("❌ start test error:", err.response?.data || err.message);
      alert("Could not start test. Please try again.");
    } finally {
      setStartingTestId(null);
    }
  };

  if (loading) {
    return (
      <div className="text-center mt-5">⏳ Loading scheduled tests...</div>
    );
  }

  return (
    <div className="container mt-4 font-poppins">
      {/* ---------------- Scheduled Tests ---------------- */}
      <h2 className="text-center fw-bold mb-4" style={{ fontSize: "2rem" }}>
        Scheduled Tests
      </h2>

      {tests.length === 0 ? (
        <div className="text-center fw-bold mb-5">
          <img
            src="https://cdn-icons-png.flaticon.com/512/4076/4076503.png"
            alt="Test Illustration"
            style={{ maxWidth: "150px", marginBottom: "20px" }}
          />
          <div
            className="mt-3"
            style={{ fontSize: "1.5rem", fontWeight: "500" }}
          >
            No upcoming tests found.
          </div>
        </div>
      ) : (
        <div className="d-flex flex-column gap-4 mb-5">
          {tests.map((test, index) => {
            const startTime = new Date(test.start_time);
            const endTime = new Date(test.end_time);
            const now = new Date();

            const isExpired = now > endTime;
            const isTooEarly = now < startTime;

            let buttonText = "Start Test";
            if (isExpired) buttonText = "Test Expired";
            else if (isTooEarly) buttonText = "Not Yet Available";

            return (
              <motion.div
                key={test._id}
                className="card custom-card"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <div className="card-body d-flex flex-column">
                  <h4 className="card-title mb-3">{test.title}</h4>

                  <p className="card-text mb-1">
                    <strong>Start:</strong>{" "}
                    {startTime.toLocaleString("en-IN", {
                      timeZone: "Asia/Kolkata",
                    })}
                  </p>
                  <p className="card-text mb-1">
                    <strong>End:</strong>{" "}
                    {endTime.toLocaleString("en-IN", {
                      timeZone: "Asia/Kolkata",
                    })}
                  </p>

                  <div className="mt-auto d-flex justify-content-end">
                    <button
                      className="btn btn-primary shadow-sm"
                      disabled={
                        isExpired || isTooEarly || startingTestId === test._id
                      }
                      onClick={() => handleStartTest(test)}
                    >
                      {startingTestId === test._id
                        ? "Launching..."
                        : buttonText}
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* ---------------- Viva Results ---------------- */}
      {/* ---------------- Viva Results ---------------- */}
      <h2
        className="text-center fw-bold mb-4 text-primary"
        style={{ fontSize: "2rem" }}
      >
        Viva Results
      </h2>

      <div className="row g-4 mb-5">
        {vivaResults.map((result, index) => {
          const totalScore =
            result.totalScore && result.detailedBreakdown
              ? Number(result.totalScore).toFixed(2)
              : null;
          const maxScore = result.detailedBreakdown
            ? result.detailedBreakdown.length * 10
            : null;
          const percentage =
            totalScore && maxScore
              ? ((Math.round(totalScore * (result?.detailedBreakdown?.length || 1)) / maxScore) * 100).toFixed(1)
              : null;

          return (
            <div key={result._id} className="col-md-6">
              <motion.div
                className="card shadow-lg border-0 rounded-4 p-3 h-100"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <div className="card-body text-center">
                  {/* Candidate / Title */}
                  <h5 className="fw-bold text-primary mb-2">
                    {testTitles[result.testId] || "Fetching title..."}
                  </h5>

                  {/* Viva Date */}
                  <span
                    className="text-muted d-block mb-3"
                    style={{ fontSize: "0.9rem" }}
                  >
                    <strong>Date:</strong>{" "}
                    {result.vivaDate
                      ? new Date(result.vivaDate).toLocaleString("en-IN")
                      : "N/A"}
                  </span>

                  {/* Score Circle + Percentage */}
                  {totalScore && maxScore ? (
                    <div>
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          justifyContent: "center",
                          width: "80px",
                          height: "80px",
                          borderRadius: "50%",
                          background: "#f8f9fa",
                          border: "3px solid #007bff",
                          fontSize: "1.2rem",
                          fontWeight: "700",
                          color: "#007bff",
                          marginBottom: "8px",
                        }}
                      >
                        {Math.round(totalScore * (result?.detailedBreakdown?.length || 1))}/{maxScore}
                      </span>
                      <br />
                      <span
                        style={{
                          fontSize: "1rem",
                          fontWeight: "600",
                          color: "#28a745",
                        }}
                      >
                        {percentage}%
                      </span>
                    </div>
                  ) : (
                    <p className="text-muted">N/A</p>
                  )}
                </div>
              </motion.div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Footer;
