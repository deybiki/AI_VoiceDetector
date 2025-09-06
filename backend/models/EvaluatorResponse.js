import mongoose from "mongoose";

const evaluatorResponseSchema = new mongoose.Schema(
  {
    sharedLinkId: {
      type: String,
      required: true,
    },
    candidateId: {
      type: String,
      required: true,
    },

    // ✅ Cumulative test score
    score: {
      type: Number,
      required: true,
    },

    // ✅ Cumulative test remarks
    // remarks: {
    //   type: String,
    //   required: true,
    //   trim: true,
    // },

    // ✅ Question-wise details
    questionwise_details: [
      {
        question_score: {
          type: Number,
          required: true,
        },
        remarks: {
          type: String,
          required: true,
          trim: true,
        },
      },
    ],
  },
  { timestamps: true }
);

export default mongoose.model("EvaluatorResponse", evaluatorResponseSchema);
