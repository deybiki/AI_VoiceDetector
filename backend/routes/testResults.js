


// routes/testResults.js
import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import VivaResult from "../models/VivaResult.js"; // ✅ Use relative path

const router = express.Router();

// POST route to save viva results
router.post("/submit-viva", async (req, res) => {
  
  console.log("🔥 Received POST /submit-viva:", req.body); // 🔍 Add this line

  const {
    testId,
    candidateId,
    questionAnswerPairs,
    totalScore,
    detailedBreakdown,
    vivaDate,
    questionAverages,
    cosineSimilarities
  } = req.body;

  try {
    const vivaResult = new VivaResult({
      testId,
      candidateId,
      questionAnswerPairs,
      totalScore,
      detailedBreakdown,
      vivaDate,
      questionAverages,
      cosineSimilarities
    });

    await vivaResult.save();
    res.status(200).json({ message: "Viva result saved successfully" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error" });
  }
});

export default router;

