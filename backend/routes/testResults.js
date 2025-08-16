// import express from "express";



// const express = require("express");
// const router = express.Router();
// const VivaResult = require("E:\AI_Viva_system\AI_VoiceDetector-master\backend\models\VivaResult.js"); // Adjust path if different

// // POST route to save viva results
// router.post("/submit-viva", async (req, res) => {
//   const {
//     candidateId,
//     questionAnswerPairs,
//     totalScore,
//     detailedBreakdown,
//     vivaDate
//   } = req.body;

//   try {
//     const vivaResult = new VivaResult({
//       candidateId,
//       questionAnswerPairs,
//       totalScore,
//       detailedBreakdown,
//       vivaDate
//     });

//     await vivaResult.save();
//     res.status(200).json({ message: "Viva result saved successfully" });
//   } catch (err) {
//     console.error(err);
//     res.status(500).json({ error: "Server error" });
//   }
// });

// module.exports = router;



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
    candidateId,
    questionAnswerPairs,
    totalScore,
    detailedBreakdown,
    vivaDate
  } = req.body;

  try {
    const vivaResult = new VivaResult({
      candidateId,
      questionAnswerPairs,
      totalScore,
      detailedBreakdown,
      vivaDate
    });

    await vivaResult.save();
    res.status(200).json({ message: "Viva result saved successfully" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error" });
  }
});

export default router;

