import mongoose from 'mongoose';

const TestAttemptSchema = new mongoose.Schema({
   student: { type: mongoose.Schema.Types.ObjectId, ref: 'Student', required: true },
   test: { type: mongoose.Schema.Types.ObjectId, ref: 'Test', required: true },
   answers: [{
      question: { type: mongoose.Schema.Types.ObjectId, ref: "Question", required: true },
      answerText: { type: String, required: true },
      reviews: [{
         evaluator: { type: mongoose.Schema.Types.ObjectId, ref: "Evaluator" },
         rating: { type: Number, min: 1, max: 5 },
         review: { type: String }
      }]
   }],
   startedAt: { type: Date, default: Date.now },
   submittedAt: { type: Date },
   status: { type: String, enum: ['attempted', 'not attempted'], default: 'not attempted' },
}, { timestamps: true });

const TestAttempt = mongoose.model('TestAttempt', TestAttemptSchema);
export default TestAttempt;