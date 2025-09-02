import express from "express";
const router = express.Router();
import {
   
   findTestAttempt,
   submitTestAttempt,
} from "../controllers/testAttempt.js";

router.get("/:studentId/:testId/fetch_test_attempt",findTestAttempt);
router.post("/:studentId/:testId/submit", submitTestAttempt);

export default router;