import mongoose from "mongoose";

const violationSchema = new mongoose.Schema({
  testId: { type: String, required: true },     // keep as String unless you want ObjectId ref
  studentId: { type: String, required: true },  // same here
  reason: { type: String, required: true },
  timestamp: { type: Date, default: Date.now }, // ✅ consistent Date type
});

export default mongoose.model("Violation", violationSchema);

