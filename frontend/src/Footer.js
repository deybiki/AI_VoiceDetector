// import React, { useEffect, useState } from "react";
// import axios from "axios";
// import "bootstrap/dist/css/bootstrap.min.css";
// import { motion } from "framer-motion";
// import "./Footer.css";

// const Footer = () => {
//   const [tests, setTests] = useState([]);
//   const [loading, setLoading] = useState(true);

//   const token = localStorage.getItem("token");
//   const studentId = localStorage.getItem("username"); // assuming scholarId is stored here

//   useEffect(() => {
//     const fetchTests = async () => {
//       try {
//         const res = await axios.get("http://localhost:5000/api/student/upcoming", {
//           withCredentials: true,
//         });
//         setTests(res.data.tests);
//       } catch (err) {
//         console.error("Error fetching tests:", err);
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchTests();
//   }, []);

//   const handleStartTest = async (testId) => {
//     try {
//       const res = await axios.post(
//         `http://localhost:5000/api/student/start/${testId}`,
//         {},
//         { withCredentials: true }
//       );

//       if (res.status === 200) {
//         // ✅ Successfully started test, open Streamlit
//         window.open(
//           `http://localhost:8501/?testId=${testId}&studentId=${studentId}`,
//           "_blank"
//         );
//       }
//     } catch (err) {
//       console.error("Error starting test:", err);
//       alert("❌ Could not start test. Please try again.");
//     }
//   };

//   if (loading) {
//     return <div className="text-center mt-5">Loading tests...</div>;
//   }

//   if (tests.length === 0) {
//     return (
//       <div className="text-center fw-bold mb-5">
//         <img
//           src="https://cdn-icons-png.flaticon.com/512/4076/4076503.png"
//           alt="No tests"
//           style={{ maxWidth: "150px", marginBottom: "20px" }}
//         />
//         <div style={{ fontSize: "1.5rem" }}>No upcoming tests found.</div>
//       </div>
//     );
//   }

//   return (
//     <div className="container mt-5">
//       <h3 className="mb-4 text-center">Scheduled Tests</h3>
//       {tests.map((test, index) => {
//         const isExpired = new Date() > new Date(test.end_time);

//         return (
//           <motion.div
//             key={test._id}
//             className="card mb-4 shadow-sm custom-card"
//             initial={{ opacity: 0, y: 40 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.4, delay: index * 0.1 }}
//           >
//             <div className="card-body d-flex flex-column">
//               <h5 className="card-title">{test.title}</h5>
//               <p className="card-text mb-1">
//                 <strong>Start:</strong>{" "}
//                 {new Date(test.start_time).toLocaleString("en-IN", {
//                   timeZone: "Asia/Kolkata",
//                 })}
//               </p>
//               <p className="card-text mb-3">
//                 <strong>End:</strong>{" "}
//                 {new Date(test.end_time).toLocaleString("en-IN", {
//                   timeZone: "Asia/Kolkata",
//                 })}
//               </p>

//               <div className="mt-auto text-end">
//                 <button
//                   className="btn btn-primary"
//                   disabled={isExpired}
//                   onClick={() => handleStartTest(test._id)}
//                 >
//                   {isExpired ? "Test Expired" : "Start Test"}
//                 </button>
//               </div>
//             </div>
//           </motion.div>
//         );
//       })}
//     </div>
//   );
// };

// export default Footer;
