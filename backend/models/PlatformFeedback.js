// backend/models/PlatformFeedback.js
import mongoose from "mongoose";

const platformFeedbackSchema = new mongoose.Schema(
  {
    candidateId: { type: String, required: true },
    rating: { type: Number, min: 1, max: 5, required: true }, // store as number
    recommendation: { type: String, default: "" },
    submittedAt: { type: Date, default: Date.now },
  },
  { timestamps: true }
);

// Force collection name (like you did for vivaresults)
const PlatformFeedback = mongoose.model(
  "PlatformFeedback",
  platformFeedbackSchema,
  "platformfeedbacks"
);

export default PlatformFeedback;
