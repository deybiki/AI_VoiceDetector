import mongoose from 'mongoose';

const ExaminerSchema = new mongoose.Schema({
   user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
   department: { type: String, required: true },
}, { timestamps: true });

const Examiner = mongoose.model('Examiner', ExaminerSchema);
export default Examiner;
