
// // routes/student.js
// import express from "express";
// import {
//    joinTest,
//    startTest,
//    submitTest,
//    getUpcomingTestsForStudent,
// } from "../controllers/studentController.js";
// import { verifyToken, authorizeRoles } from "../middlewares/authMiddleware.js"
// import { getTestStudents } from "../controllers/examinerController.js";

// const router = express.Router();

// router.get("/upcoming", verifyToken, authorizeRoles("student"), getUpcomingTestsForStudent);
// router.post("/join/:testId", verifyToken, authorizeRoles("student"), joinTest);
// router.post("/start/:testId", verifyToken, authorizeRoles("student"), startTest);
// router.post("/submit/:testId", verifyToken, authorizeRoles("student"), submitTest);
// router.get("/test/:testId/students", getTestStudents);

// export default router;


// import express from "express";
// import {
//    joinTest,
//    startTest,
//    submitTest,
//    getUpcomingTestsForStudent,
// } from "../controllers/studentController.js";
// import { verifyToken, authorizeRoles } from "../middlewares/authMiddleware.js"
// import { getTestStudents } from "../controllers/examinerController.js";
// import Student from "../models/Student.js"; // ✅ Import Student model

// const router = express.Router();

// router.get("/upcoming", verifyToken, authorizeRoles("student"), getUpcomingTestsForStudent);
// router.post("/join/:testId", verifyToken, authorizeRoles("student"), joinTest);
// router.post("/start/:testId", verifyToken, authorizeRoles("student"), startTest);
// router.post("/submit/:testId", verifyToken, authorizeRoles("student"), submitTest);
// router.get("/test/:testId/students", getTestStudents);

// // ✅ New route to fetch student photo by scholarId
// router.get("/student/:scholarId", async (req, res) => {
//   try {
//     const student = await Student.findOne({ scholarId: req.params.scholarId });
//     if (!student) return res.status(404).json({ msg: "Student not found" });

//     res.status(200).json({ photo: student.photo });
//   } catch (err) {
//     console.error("Error fetching student photo:", err);
//     res.status(500).json({ msg: "Server error" });
//   }
// });

// router.get("/student/:scholarId", async (req, res) => {
//   try {
//     const student = await Student.findOne({ scholarId: req.params.scholarId });
//     if (!student) return res.status(404).json({ msg: "Student not found" });

//     res.status(200).json({
//       photo: student.photo, // Must be a full URL (e.g., http://localhost:5000/uploads/abc123.jpg)
//     });
//   } catch (err) {
//     res.status(500).json({ msg: "Server error" });
//   }
// });

// export default router;






import express from "express";
import {
   joinTest,
   startTest,
   submitTest,
   getUpcomingTestsForStudent,
   fetchStudentId,
} from "../controllers/studentController.js";
import { verifyToken, authorizeRoles } from "../middlewares/authMiddleware.js";
import { getTestStudents } from "../controllers/examinerController.js";
import Student from "../models/Student.js";

const router = express.Router();

// router.post("/start/:testId", (req, res, next) => {
//   console.log("✅ /start/:testId route hit");
//   next(); 
// });

router.post(
  "/start/:testId",
  (req, res, next) => {
    console.log("✅ /start/:testId route hit");
    next();
  },
  verifyToken,
  authorizeRoles("student"),
  startTest
);




router.get("/upcoming", verifyToken, authorizeRoles("student"), getUpcomingTestsForStudent);
router.post("/join/:testId", verifyToken, authorizeRoles("student"), joinTest);
router.post("/start/:testId", verifyToken, authorizeRoles("student"), startTest); 
router.post("/submit/:testId", verifyToken, authorizeRoles("student"), submitTest);
router.get("/test/:testId/students", getTestStudents);


router.get("/student/:scholarId", async (req, res) => {
  try {
    const student = await Student.findOne({ scholarId: req.params.scholarId });
    if (!student) return res.status(404).json({ msg: "Student not found" });

    res.status(200).json({
      photo: student.photo, // should be a complete URL if used in frontend image
    });
  } catch (err) {
    console.error("Error fetching student photo:", err);
    res.status(500).json({ msg: "Server error" });
  }
});

router.get("/:scholarId/fetchId", fetchStudentId);

export default router;
