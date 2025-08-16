import mongoose from 'mongoose';

const StudentSchema = new mongoose.Schema({
   user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
   image: { type: String },
   scholarId: { type: String, required: true, unique: true },
   department: { type: String, required: true },
}, { timestamps: true });

const Student = mongoose.model('Student', StudentSchema);
export default Student;
