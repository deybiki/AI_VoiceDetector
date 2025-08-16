import React, { useEffect, useRef } from "react";
import { motion, useAnimation } from "framer-motion";
import Lottie from "lottie-react";
import "./Upload.css";

// 👉 Replace this with your actual animation JSON file path
import vivaAnimation from "../../assets/lotties/viva_animation.json";

function Upload() {
  const leftControls = useAnimation();
  const rightControls = useAnimation();
  const ref = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          leftControls.start({ opacity: 1, x: 0 });
          rightControls.start({ opacity: 1, x: 0 });
        }
      },
      { threshold: 0.3 }
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [leftControls, rightControls]);

  return (
    <div className="container" ref={ref}>
      <div className="row">
        {/* ✅ Left Side with horizontal transition + hover zoom */}
        <motion.div
          className="col-6 d-flex justify-content-center align-items-center"
          initial={{ opacity: 0, x: -100 }}
          animate={leftControls}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <div
            className="p-4 "
            style={{
              borderRadius: "20px",
              boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
              width: "100%",
              maxWidth: "550px",
            }}
          >
            <h4
              className="fw-bold display-6 mb-3 text-center"
              style={{ fontFamily: "'Playfair Display', serif" }}
            >
              Smarter Viva Management
            </h4>
            <p
              className="text-dark fs-5 text-center"
              style={{ fontFamily: "Poppins, sans-serif" }}
            >
              A platform to create, conduct, and evaluate viva exams seamlessly.
            </p>

            {[
              "Assign tests with timing and custom questions",
              "Students record responses directly on the platform",
              "Choose AI or human evaluation",
            ].map((text, idx) => (
              <h5 key={idx} className="mb-3 text-primary text-center">
                <i
                  className="fa fa-chevron-circle-right me-2"
                  aria-hidden="true"
                ></i>
                {text}
              </h5>
            ))}
          </div>
        </motion.div>

        {/* ✅ Right Side with Lottie Animation */}
        <motion.div
          className="col-6 mt-4 d-flex justify-content-center align-items-center"
          style={{ minHeight: "60vh" }}
          initial={{ opacity: 0, x: 100 }}
          animate={rightControls}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <div
            className=""
            style={{ width: "100%", maxWidth: "500px" }}
          >
            <Lottie
              animationData={vivaAnimation}
              loop={true}
              autoplay={true}
              style={{ width: "100%", height: "100%" }}
            />
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default Upload;
