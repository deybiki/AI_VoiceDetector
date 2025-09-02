// import mongoose from 'mongoose';
// const mongoose = require("mongoose");

// const VivaResultSchema = new mongoose.Schema({
//   candidateId: { type: String, required: true },
//   vivaDate: { type: Date, default: Date.now },
//   questionAnswerPairs: [
//     {
//       question: String,
//       answer: String,
//       score: Number,
//       feedback: String
//     }
//   ],
//   totalScore: Number,
//   detailedBreakdown: Object
// });

// module.exports = mongoose.model("VivaResult", VivaResultSchema);


// import mongoose from "mongoose";

// const VivaResultSchema = new mongoose.Schema({
//   candidateId: String,
//   questionAnswerPairs: Array,
//   totalScore: Number,
//   detailedBreakdown: Object,
//   vivaDate: Date
// });

// const VivaResult = mongoose.model("VivaResult", VivaResultSchema);
// export default VivaResult;


import mongoose from "mongoose";

const vivaResultSchema = new mongoose.Schema({
  testId: { type: String, required: true }, 
  candidateId: { type: String, required: true },
  vivaDate: { type: Date, required: true },
  questionAnswerPairs: [
    {
      question: String,
      answer: String,
      score: Number,
      feedback: String
      
    }
  ],
  totalScore: Number,
  // ✅ Status field added
  status: {
    type: String,
    enum: ["Not Evaluated", "Evaluated"], // restrict values
    default: "Not Evaluated", // default jab naya record create hoga
  },
  questionAverages: [Number],
  cosineSimilarities: [Number],
  detailedBreakdown: Object,
});

// const VivaResult = mongoose.model("VivaResult", vivaResultSchema);
const VivaResult = mongoose.model("VivaResult", vivaResultSchema, "vivaresults"); // 👈 Force collection name

export default VivaResult;


