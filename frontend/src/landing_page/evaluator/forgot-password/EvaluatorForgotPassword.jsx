import { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const EvaluatorForgotPassword = () => {
   const [email, setEmail] = useState("");
   const [step, setStep] = useState(1); // 1: enter email, 2: enter OTP + password
   const [otp, setOtp] = useState("");
   const [newPassword, setNewPassword] = useState("");
   const [loading, setLoading] = useState(false);
   const navigate = useNavigate();

   const sendOtp = async (e) => {
      e.preventDefault();
      setLoading(true);
      try {
         await axios.post("http://localhost:5000/api/evaluator/forgot-password", { email });
         toast.success("OTP sent to your email");
         setStep(2);
      } catch (err) {
         toast.error(err?.response?.data?.msg || "Failed to send OTP");
      }
      setLoading(false);
   };

   const resetPassword = async (e) => {
      e.preventDefault();
      setLoading(true);
      try {
         await axios.post("http://localhost:5000/api/evaluator/reset-password", {
            email,
            otp,
            newPassword,
         });
         toast.success("Password changed! Please login.");
         setTimeout(() => navigate("/evaluator/login"), 1200);
      } catch (err) {
         toast.error(err?.response?.data?.msg || "Failed to reset password");
      }
      setLoading(false);
   };

   return (
      <div className="container mt-5" style={{ maxWidth: "400px" }}>
         <h3 className="text-center text-primary mb-4">Forgot Password</h3>
         {step === 1 ? (
            <form onSubmit={sendOtp}>
               <div className="mb-3">
                  <label className="form-label fw-semibold">Email</label>
                  <input
                     type="email"
                     className="form-control"
                     required
                     value={email}
                     onChange={e => setEmail(e.target.value)}
                     placeholder="Enter your evaluator email"
                  />
               </div>
               <div className="d-grid">
                  <button className="btn btn-primary" type="submit" disabled={loading}>
                     {loading ? "Sending..." : "Send OTP"}
                  </button>
               </div>
            </form>
         ) : (
            <form onSubmit={resetPassword}>
               <div className="mb-3">
                  <label className="form-label fw-semibold">OTP</label>
                  <input
                     type="text"
                     className="form-control"
                     required
                     value={otp}
                     onChange={e => setOtp(e.target.value)}
                     placeholder="Enter OTP sent to email"
                  />
               </div>
               <div className="mb-3">
                  <label className="form-label fw-semibold">New Password</label>
                  <input
                     type="password"
                     className="form-control"
                     required
                     value={newPassword}
                     onChange={e => setNewPassword(e.target.value)}
                     placeholder="Enter new password"
                  />
               </div>
               <div className="d-grid">
                  <button className="btn btn-success" type="submit" disabled={loading}>
                     {loading ? "Resetting..." : "Reset Password"}
                  </button>
               </div>
            </form>
         )}
         <div className="text-center mt-4">
            <a href="/evaluator/login" className="text-primary">Back to Login</a>
         </div>
      </div>
   );
};

export default EvaluatorForgotPassword;
