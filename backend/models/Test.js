import mongoose from 'mongoose';

const TestSchema = new mongoose.Schema({
   title: { type: String, required: true },
   examiner: { type: mongoose.Schema.Types.ObjectId, ref: 'Examiner', required: true },

   evaluators: [{ type: mongoose.Schema.Types.ObjectId, ref: "Evaluator" }],
   department: { type: String },
   sharedLinkId: { type: String, unique: true },
   questions: [{ type: mongoose.Schema.Types.ObjectId, ref: "Question" }],
   students: [{ type: mongoose.Schema.Types.ObjectId, ref: "Student" }],
   pendingEvaluators: [{
      email: { type: String },
      inviteToken: { type: String },
      invitedAt: { type: Date }
   }],
   createdAt: { type: Date, default: Date.now },
   start_time: { type: Date, required: true },
   end_time: { type: Date, required: true }
}, { timestamps: true });

export default mongoose.model('Test', TestSchema);
