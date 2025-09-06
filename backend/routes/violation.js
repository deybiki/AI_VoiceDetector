import express from "express";
import Violation from "../models/Violation.js";

const router = express.Router();

// POST /api/log-violation
router.post("/log-violation", async (req, res) => {
  try {
    const { testId, studentId, reason, ts } = req.body;

    const violation = new Violation({
      testId,
      studentId,
      reason,
      timestamp: ts ? new Date(ts) : new Date() // ✅ ensure Date type
    });

    await violation.save();
    res.status(201).json({ success: true, violation });
  } catch (err) {
    console.error("Violation log error:", err);
    res.status(500).json({ success: false, error: "Failed to log violation" });
  }
});

export default router;


