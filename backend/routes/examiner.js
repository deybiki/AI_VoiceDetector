
// routes/examiner.js
import express from "express";
import {
   inviteStudents,
   removeStudent,
   getTestStudents,
   getTests
} from "../controllers/examinerController.js";

import { verifyToken, authorizeRoles } from "../middlewares/authMiddleware.js"
import { addPendingEvaluator } from "../controllers/evaluatorController.js";
import { addStudents, removeQuestion, removeTest } from "../controllers/testController.js";

const router = express.Router();

router.post("/invite-evaluator/:testId", verifyToken, authorizeRoles("examiner"), addPendingEvaluator)
router.post("/invite/:testId", verifyToken, authorizeRoles("examiner"), inviteStudents);

router.post("/:testId/students", verifyToken, authorizeRoles("examiner"), addStudents);
router.get("/:testId/students", verifyToken, authorizeRoles("examiner"), getTestStudents);
router.get("/get-tests", verifyToken, authorizeRoles("examiner"), getTests)


router.delete("/remove/:testId/student/:studentId", verifyToken, authorizeRoles("examiner"), removeStudent);
router.delete("/:testId/question/:questionId", verifyToken, authorizeRoles("examiner"), removeQuestion);
router.delete("/remove/test/:testId", verifyToken, authorizeRoles("examiner"), removeTest)

export default router;