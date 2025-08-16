import mongoose from "mongoose";

const AnswerSchema = new mongoose.Schema({
   studentTestId: { type: mongoose.Schema.Types.ObjectId, ref: 'StudentTest', required: true },
   questionId: { type: mongoose.Schema.Types.ObjectId, ref: 'Question', required: true },
   audioFilePath: { type: String, required: true },
   transcript_text: { type: String },
   score: { type: Number }
}, { timestamps: true });

const Answer = mongoose.model('Answer', AnswerSchema);
export default Answer;
