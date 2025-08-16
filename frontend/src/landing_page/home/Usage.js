import React, { useEffect, useRef } from "react";
import { motion, useAnimation } from "framer-motion";
import "./Usage.css";
import Lottie from "lottie-react";
import vivaAnimation from "../../assets/lotties/viva_animation2.json";

function Usage() {
  const controls = useAnimation();
  const ref = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          controls.start({ opacity: 1, y: 0 });
        }
      },
      { threshold: 0.2 }
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [controls]);

  const [activeTab, setActiveTab] = React.useState("professors");

  const tabStyle = (tab) => ({
    padding: "10px 20px",
    cursor: "pointer",
    fontWeight: "500",
    color: activeTab === tab ? "#000" : "#3b5bdb",
    borderBottom: activeTab === tab ? "2px solid #3b5bdb" : "none",
    backgroundColor: "transparent",
    border: "none",
    outline: "none",
  });

  return (
    <motion.div
      className="container"
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={controls}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <div className="row">
        {/* ✅ Left Animation */}
        <div className="col-6 d-flex justify-content-center align-items-center mt-5">
          <div className="mb-5" style={{ maxWidth: "100%", width: "700px" }}>
            <Lottie animationData={vivaAnimation} loop={true} />
          </div>
        </div>

        {/* ✅ Right Side Content */}
        <div
          className="col-6 ps-5"
          style={{
            maxWidth: "700px",
            margin: "auto",
            fontFamily: "sans-serif",
            borderRadius: "12px",
            padding: "10px",
          }}
        >
          <h2
            className="fw-bold mb-3"
            style={{
              fontFamily: "'Playfair Display', serif",
              letterSpacing: "0.5px",
              WebkitFontSmoothing: "antialiased",
            }}
          >
            Empowering professors and students
            <br />
            with a seamless viva experience
          </h2>

          <p style={{ color: "#555", fontSize: "16px" }}>
            Professors can create and assign viva tests with ease, while
            students can record voice responses from anywhere
            <br />
            making the viva process efficient, secure, and flexible.
          </p>

          <div
            className="p-3 mt-3"
            style={{
              border: "1px solid #dfe3e6",
              borderRadius: "10px",
              backgroundColor: "#fff",
              maxHeight: "250px",
              overflowY: "auto",
            }}
          >
            {/* Tabs */}
            <div
              style={{
                display: "flex",
                borderBottom: "1px solid #ccc",
                marginBottom: "15px",
              }}
            >
              <button
                style={tabStyle("professors")}
                onClick={() => setActiveTab("professors")}
              >
                For Professors
              </button>
              <button
                style={tabStyle("students")}
                onClick={() => setActiveTab("students")}
              >
                For Students
              </button>
            </div>

            {/* Tab Content */}
            {activeTab === "professors" && (
              <div>
                <ul style={{ paddingLeft: "20px", lineHeight: "1.8" }}>
                  <li>
                    <strong>Create Viva Test</strong>
                    <br />
                    Set test title, duration (start/end time), and department.
                    <br />
                    Define viva questions (currently hardcoded or entered
                    manually).
                  </li>

                  <li>
                    <strong>Assign Tests to Specific Students</strong>
                    <br />
                    Select specific students by email or name.
                    <br />
                    Assign one test to multiple students simultaneously.
                  </li>

                  <li>
                    <strong>Remove Students</strong>
                    <br />
                    Remove any registered student from the database if needed
                    (e.g., incorrect or inactive account).
                  </li>

                  <li>
                    <strong>View Test Results</strong>
                    <br />
                    Access submitted responses.
                    <br />
                    See AI-generated analysis of student answers (e.g.,
                    percentage of AI-generated content vs. human).
                  </li>

                  <li>
                    <strong>Assign Human Evaluator (Optional)</strong>
                    <br />
                    Optionally assign another professor as a human evaluator.
                    <br />
                    Evaluator receives notification and test access credentials.
                  </li>
                </ul>
              </div>
            )}

            {activeTab === "students" && (
              <div>
                <ul style={{ paddingLeft: "20px", lineHeight: "1.8" }}>
                  <li>
                    <strong>View Upcoming Viva Tests</strong>
                    <br />
                    Students can see test notifications on their dashboard
                    including test title, professor name, and the test window.
                  </li>

                  <li>
                    <strong>Give Voice-Based Viva</strong>
                    <br />
                    Within the assigned time range, students can start the test,
                    turn on their camera, and answer viva questions via voice
                    input.
                  </li>

                  <li>
                    <strong>See AI Authenticity Report</strong>
                    <br />
                    After submitting the test, students can view an AI-generated
                    analysis showing how much of their response was human or
                    AI-like.
                  </li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default Usage;
