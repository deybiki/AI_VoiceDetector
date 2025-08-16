import mongoose from 'mongoose';

const QuestionSchema = new mongoose.Schema({
   testId: { type: mongoose.Schema.Types.ObjectId, ref: 'Test', required: true },
   questionText: { type: String, required: true },
}, { timestamps: true });

const Question = mongoose.model('Question', QuestionSchema);
export default Question;
