import mongoose from "mongoose";

const evaluatorResponseSchema = new mongoose.Schema(
  {
    sharedLinkId: {
      type: String,   // ab sirf string store hogi
      required: true,
    },
    candidateId: {
      type: String,   // ab sirf string store hoga
      required: true,
    },
    score: {
      type: Number,   // integer score
      required: true,
    },
    remarks: {
      type: String,   // textual feedback
      required: true,
      trim: true,
    },
  },
  { timestamps: true }
);

export default mongoose.model("EvaluatorResponse", evaluatorResponseSchema);
