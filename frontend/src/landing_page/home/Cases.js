import React, { useState, useRef, useEffect } from "react";
import { motion, useAnimation } from "framer-motion";
import "./Cases.css";

const caseData = [
  {
    title: "⏰ Late Join – Test Denied",
    heading: "Strict Time Compliance: No Late Entries",
    content:
      "Each test has a specific start and end time. If a student attempts to join even a minute late, access is automatically denied and the test is marked as 'Missed'. This enforces discipline and prevents students from using leaked questions to gain an unfair advantage.",
    btnText: "Understand the Rules",
    img: "proj_img/time.png", // 🔄 Replace with your image path
  },
  {
    title: "🤖 AI vs Human Scoring",
    heading: "AI Detection with Human Cross-Check",
    content:
      "All submitted voice responses are first analyzed using an LLM-based scoring engine to detect AI-generated content. If flagged, the test is reviewed by a human evaluator who confirms the results. This dual-layered system ensures fairness, transparency, and reliability in scoring.",
    btnText: "Learn How It Works",
    img: "proj_img/ai_human31.png", // 🔄 Replace with your image path
  },
  {
    title: "🎥 Video Identity Verification",
    heading: "Live Video Recording to Prevent Impersonation",
    content:
      "The candidate’s webcam remains active during the viva. A short video is recorded and linked with the voice response. This ensures the registered student is the one taking the test, discouraging impersonation and enhancing credibility.",
    btnText: "See the Safeguards",
    img: "proj_img/webcam.png", // 🔄 Replace with your image path
  },
];

const Cases = () => {
  const [selectedCaseIndex, setSelectedCaseIndex] = useState(0);
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

  const selectedCase = caseData[selectedCaseIndex];

  return (
    <motion.div
      className="container py-5"
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={controls}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <div className="text-center mb-5 mt-5">
        <h1
          className="fw-bold display-5"
          style={{
            fontFamily: "'Playfair Display', serif",
            letterSpacing: "0.5px",
            WebkitFontSmoothing: "antialiased",
          }}
        >
          Strengthening Credibility in AI-Based Viva Tests
        </h1>
      </div>
      <div className="row align-items-stretch">
        {/* ✅ Case Buttons */}
        <div className="col-md-4 mb-4 d-flex flex-column justify-content-between">
          {caseData.map((c, i) => (
            <button
              key={i}
              className={`btn mb-3 mt-3 text-start d-flex align-items-center justify-content-start px-3 py-5 w-100 zoom-btn-hover ${
                selectedCaseIndex === i
                  ? "btn-primary text-white"
                  : "btn-outline-secondary text-black"
              }`}
              style={{
                borderRadius: "10px",
                fontWeight: 500,
                minHeight: "60px",
                transition: "transform 0.3s ease, box-shadow 0.3s ease",
              }}
              onClick={() => setSelectedCaseIndex(i)}
            >
              <i className="fa fa-bars me-4" aria-hidden="true"></i>
              <span className="text-wrap text-break">{c.title}</span>
            </button>
          ))}
        </div>

        {/* ✅ Case Image */}
        <div className="col-md-4 d-flex align-items-stretch">
          <div className="me-md-4 mb-3 mb-md-0" style={{ flex: "1 1 40%" }}>
            <img
              src={selectedCase.img}
              alt="case"
              className="img-fluid rounded h-100 w-100 object-fit-cover "
              style={{
                objectFit: "cover",
                transition: "transform 0.3s ease, boxShadow 0.3s ease",
                borderRadius: "12px",
              }}
            />
          </div>
        </div>

        {/* ✅ Case Content */}
        <div className="col-md-4 d-flex align-items-stretch right">
          <div
            style={{ flex: "1 1 60%" }}
            className="d-flex flex-column justify-content-between "
          >
            <div>
              <h4 className="fw-bold mb-3">{selectedCase.heading}</h4>
              <p className="mb-4" style={{ lineHeight: "1.7" }}>
                {selectedCase.content}
              </p>
            </div>
            <button className="btn btn-primary align-self-start py-3">
              {selectedCase.btnText}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Cases;
