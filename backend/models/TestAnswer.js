import mongoose from 'mongoose';

const TestAnswerSchema = new mongoose.Schema({
   testId: { type: mongoose.Schema.Types.ObjectId, ref: 'Test', required: true },
   answerText: { type: String, required: true },
}, { timestamps: true });

const TestAnswer = mongoose.model('TestAnswer', TestAnswerSchema);
export default TestAnswer;
