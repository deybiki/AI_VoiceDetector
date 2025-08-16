import mongoose from "mongoose";

const EvaluatorSchema = new mongoose.Schema({
   name: { type: String },
   email: { type: String, required: true, unique: true },
   password: { type: String, required: true },
   resetPasswordToken: String,
   resetPasswordExpires: Date,
}, { timestamps: true });

const Evaluator = mongoose.model('Evaluator', EvaluatorSchema);
export default Evaluator