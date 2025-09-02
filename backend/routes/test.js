
// routes/test.js
import express from "express";
import { createTest, addQuestion, addQuestions, getTest, addStudents, removeQuestion,findtestfromId } from "../controllers/testController.js";
import { verifyToken, authorizeRoles } from "../middlewares/authMiddleware.js"
import { removeStudent } from "../controllers/examinerController.js";
import upload from "../middlewares/multerMiddleware.js";
const router = express.Router();

router.post("/create", verifyToken, authorizeRoles("examiner"), createTest);
router.post("/:testId/question", verifyToken, authorizeRoles("examiner"), addQuestion);
router.post("/:testId/questions", verifyToken, authorizeRoles("examiner"),upload.single("file"), addQuestions);
router.get("/:testId", verifyToken, authorizeRoles("examiner"), getTest);
router.get("/:sharedLinkId/title", findtestfromId);


export default router;
