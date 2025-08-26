// backend/platformFeedback.js
import express from "express";
import PlatformFeedback from "./models/PlatformFeedback.js";

const router = express.Router();

// POST /api/feedback/platform
router.post("/platform", async (req, res) => {
  try {
    const { candidateId, rating, recommendation, timestamp } = req.body;

    if (!candidateId || !rating) {
      return res.status(400).json({ error: "candidateId and rating are required" });
    }

    const doc = new PlatformFeedback({
      candidateId,
      rating,
      recommendation: recommendation || "",
      submittedAt: timestamp ? new Date(timestamp) : new Date(),
    });

    await doc.save();
    res.status(200).json({ message: "Platform feedback saved", id: doc._id });
  } catch (err) {
    console.error("Platform feedback save error:", err);
    res.status(500).json({ error: "Server error" });
  }
});

// GET /api/feedback/platform
router.get("/platform", async (req, res) => {
  const { candidateId } = req.query;
  const q = candidateId ? { candidateId } : {};
  const items = await PlatformFeedback.find(q).sort({ createdAt: -1 }).lean();
  res.json(items);
});

export default router;
