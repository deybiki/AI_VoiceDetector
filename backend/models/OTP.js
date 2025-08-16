import mongoose from "mongoose";

const otpSchema = new mongoose.Schema({
   otp: { type: String, required: true },
   email: { type: String, required: true }
}, { timestamps: true })

export default mongoose.model('OTP', otpSchema)