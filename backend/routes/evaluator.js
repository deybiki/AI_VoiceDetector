import express from "express";
import {
   registerFromInvite,
   evaluatorLogin,
   getEvaluatorTests,
   getTestAttempts,
   reviewStudentAnswer,
   getTestAttempt,
   sendForgotPasswordOtp,
   resetEvaluatorPassword,
   acceptEvaluatorAssignment,
   deleteEvaluator,
   deleteMe,
} from "../controllers/evaluatorController.js";

import { requireEvaluatorAuth } from "../middlewares/evaluatorMiddleware.js";

const router = express.Router();

router.post("/invite-register", registerFromInvite); // body: testId, token, name, password
router.post("/login", evaluatorLogin);

router.get("/tests", requireEvaluatorAuth, getEvaluatorTests);
router.get("/test/:testId/attempts", requireEvaluatorAuth, getTestAttempts);
router.post("/review/:testAttemptId/:questionId", requireEvaluatorAuth, reviewStudentAnswer);
router.get("/test-attempt/:attemptId", requireEvaluatorAuth, getTestAttempt)

router.post("/forgot-password", sendForgotPasswordOtp);
router.post("/reset-password", resetEvaluatorPassword);

router.get('/accept', acceptEvaluatorAssignment);

router.delete("/me", requireEvaluatorAuth, deleteMe)

export default router;