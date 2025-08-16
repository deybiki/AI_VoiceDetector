import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const EvaluatorLogin = () => {
   const [form, setForm] = useState({ email: "", password: "" });
   const navigate = useNavigate();
   const [loading, setLoading] = useState(false);

   const handleLogin = async (e) => {
      e.preventDefault();
      setLoading(true);
      try {
         await axios.post(
            "http://localhost:5000/api/evaluator/login",
            {
               email: form.email,
               password: form.password,
            },
            { withCredentials: true }
         );
         toast.success("Login successful");
         setTimeout(() => navigate("/evaluator/dashboard"), 1000);
      } catch (err) {
         toast.error(err?.response?.data?.msg || "Failed to login");
      } finally {
         setLoading(false);
      }
   };

   return (
      <div className="container d-flex justify-content-center align-items-center flex-column mt-5">
         <h3 className="mb-4 text-primary">Evaluator Login</h3>

         <form onSubmit={handleLogin} style={{ maxWidth: "400px", width: "100%" }}>
            <div className="mb-3">
               <label className="form-label fw-semibold">Email</label>
               <input
                  type="email"
                  className="form-control"
                  placeholder="Enter your email"
                  required
                  value={form.email}
                  onChange={(e) =>
                     setForm((f) => ({ ...f, email: e.target.value }))
                  }
               />
            </div>

            <div className="mb-3">
               <label className="form-label fw-semibold">Password</label>
               <input
                  type="password"
                  className="form-control"
                  placeholder="Enter your password"
                  required
                  value={form.password}
                  onChange={(e) =>
                     setForm((f) => ({ ...f, password: e.target.value }))
                  }
               />
            </div>

            <div className="text-center mt-2 mb-2">
               <a href="/evaluator/forgot-password" className="text-primary">
                  Forgot Password?
               </a>
            </div>


            <div className="d-grid">
               <button
                  className="btn btn-primary"
                  type="submit"
                  disabled={loading}
               >
                  {loading ? "Logging in..." : "Login"}
               </button>
            </div>
         </form>

         <div className="text-center mt-4">
            <p className="text-muted">
               Don't have an account?{" "}
               <a
                  href="http://localhost:3000/evaluator/invite"
                  className="text-primary fw-bold"
               >
                  Register here
               </a>
            </p>
         </div>
      </div>
   );
};

export default EvaluatorLogin;
