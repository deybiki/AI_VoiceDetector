

import React, { useEffect, useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { motion } from "framer-motion";
import "./Footer.css";

const Footer = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [startingTestId, setStartingTestId] = useState(null);

  const token = localStorage.getItem("token");
  const studentId = localStorage.getItem("username"); // assuming scholarId

  useEffect(() => {
    const fetchTests = async () => {
      try {
        const res = await axios.get("http://localhost:5000/api/student/upcoming", {
          withCredentials: true,
        });
        setTests(res.data.tests);
      } catch (err) {
        console.error("❌ Error fetching upcoming tests:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTests();
  }, []);



// await axios.post(`http://localhost:5000/api/student/start/${testId}`, {}, { withCredentials: true });




  // const handleStartTest = async (testId) => {
  //   setStartingTestId(testId); // disable button while waiting
  //   console.log("🔄 Attempting to start test:", testId);
  //   console.log("📛 Student ID (from localStorage):", studentId);

  //   try {
  //     const res = await axios.post(
  //       `http://localhost:5000/api/student/start/${testId}`,
  //       {},
  //       { withCredentials: true }
  //     );

  //     if (res.status === 200) {
  //       console.log("✅ Test started successfully:", res.data);
  //       const streamlitUrl = `http://localhost:8501/?studentId=${studentId}&testId=${testId}`;
  //       window.open(streamlitUrl, "_blank");
  //     } else {
  //       alert("⚠️ Could not start the test. Server returned unexpected response.");
  //     }
  //   } catch (err) {
  //     console.error("❌ Error starting test:", err);
  //     alert("Could not start test. Please try again.");
  //   } finally {
  //     setStartingTestId(null);
  //   }
  // };




//     const handleStartTest = async (testId) => {
//       setStartingTestId(testId);
//       console.log("🔄 Attempting to start test:", testId);
//       console.log("📛 Student ID (from localStorage):", studentId);

//       try {
//     // 👉 FIRST call /join/:testId to create TestAttempt if not exists
//         await axios.post(
//            `http://localhost:5000/api/student/join/${testId}`,
//         {},
//         { withCredentials: true }
//     );
//         console.log("✅ Joined test");

//     // 👉 THEN call /start/:testId
//         const res = await axios.post(
//           `http://localhost:5000/api/student/start/${testId}`,
//           {},
//           { withCredentials: true }
//     );

//         if (res.status === 200) {
//           console.log("✅ Test started successfully:", res.data);
//           // const streamlitUrl = `http://localhost:8501/?studentId=${studentId}&testId=${testId}`;
//           const streamlitUrl = `http://localhost:8501/interview_app?testId=${test.sharedLinkId}&studentId=${studentId}`;
//           window.open(streamlitUrl, "_blank");
//     }   else {
//           alert("⚠️ Could not start the test. Server returned unexpected response.");
//     }
//   }  catch (err) {
//      console.error("❌ Error starting test:", err);
//      alert("Could not start test. Please try again.");
//   }  finally {
//      setStartingTestId(null);
//   }
// };


//     const handleStartTest = async (test) => {
//        setStartingTestId(test._id);
//        console.log("🔄 Attempting to start test:", test._id);
//        console.log("📛 Student ID (from localStorage):", studentId);

//        try {
//            await axios.post(
//               `http://localhost:5000/api/student/join/${test._id}`,
//           {},
//            { withCredentials: true }
//     );
//            console.log("✅ Joined test");

//            const res = await axios.post(
//             `http://localhost:5000/api/student/start/${test._id}`,
//              {},
//                { withCredentials: true }
//     );

//            if (res.status === 200) {
//              console.log("✅ Test started successfully:", res.data);
//              const streamlitUrl = `http://localhost:8501/interview_app?testId=${test.sharedLinkId}&studentId=${studentId}`;
//              window.open(streamlitUrl, "_blank");
//     }      else {
//              alert("⚠️ Could not start the test. Server returned unexpected response.");
//     }
//   } catch (err) {
//     console.error("❌ Error starting test:", err);
//     alert("Could not start test. Please try again.");
//   } finally {
//     setStartingTestId(null);
//   }
// };

  const handleStartTest = async (test) => {
  const testMongoId = test._id;  // For backend APIs
  const sharedLinkId = test.sharedLinkId;  // For Streamlit

  setStartingTestId(testMongoId);
  console.log("🔄 Attempting to start test:", testMongoId);
  console.log("📛 Student ID (from localStorage):", studentId);

  try {
    // 1. JOIN test using _id
    await axios.post(
      `http://localhost:5000/api/student/join/${testMongoId}`,
      {},
      { withCredentials: true }
    );
    console.log("✅ Joined test");

    // 2. START test using _id
    const res = await axios.post(
      `http://localhost:5000/api/student/start/${testMongoId}`,
      {},
      { withCredentials: true }
    );

    // if (res.status === 200) {
    //   console.log("✅ Test started successfully:", res.data);
    //   const streamlitUrl = `http://localhost:8501/interview_app?testId=${sharedLinkId}&studentId=${studentId}`;
    //   window.open(streamlitUrl, "_blank");
    // } 
     
     if (res.status === 200) {
  console.log("✅ Test started successfully:", res.data);
  const streamlitUrl = `http://localhost:8501/?testId=${test.sharedLinkId}&studentId=${studentId}`;
;  

  window.open(streamlitUrl, "_blank");
}

    
      else {
      alert("⚠️ Could not start the test. Server returned unexpected response.");
    }
  } catch (err) {
    console.error("❌ Error starting test:", err);
    alert("Could not start test. Please try again.");
  } finally {
    setStartingTestId(null);
  }
};



   

  if (loading) {
    return <div className="text-center mt-5">⏳ Loading scheduled tests...</div>;
  }

  if (tests.length === 0) {
    return (
      <div className="text-center fw-bold mb-5">
        <img
          src="https://cdn-icons-png.flaticon.com/512/4076/4076503.png"
          alt="Test Illustration"
          style={{ maxWidth: "150px", marginBottom: "20px" }}
        />
        <div className="mt-3" style={{ fontSize: "1.5rem", fontWeight: "500" }}>
          No upcoming tests found.
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4 font-poppins">
      <h2 className="text-center fw-bold mb-4" style={{ fontSize: "2rem" }}>
        Scheduled Tests
      </h2>

      <div className="d-flex flex-column gap-4">
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
                  {startTime.toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}
                </p>
                <p className="card-text mb-1">
                  <strong>End:</strong>{" "}
                  {endTime.toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}
                </p>

                <div className="mt-auto d-flex justify-content-end">
                  <button
                    className="btn btn-primary shadow-sm"
                    disabled={isExpired || isTooEarly || startingTestId === test._id}
                    onClick={() => handleStartTest(test)}
                  >
                    {startingTestId === test._id ? "Launching..." : buttonText}
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default Footer;
