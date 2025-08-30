


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


