import { useState } from "react";
import axios from "axios";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const EvaluatorInvite = () => {
  const [params] = useSearchParams();
  const testId = params.get("testId");
  const token = params.get("token");
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", password: "" });
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(
        "http://localhost:5000/api/evaluator/invite-register",
        {
          testId,
          token,
          name: form.name,
          password: form.password,
        },
        { withCredentials: true }
      );

      toast.success("Registration successful! Redirecting...");
      setTimeout(() => navigate("/evaluator/dashboard"), 1200);
    } catch (err) {
      const msg = err?.response?.data?.msg || "";
      console.log("msg kya hai", msg);
      if (msg.toLowerCase().includes("invalid or expired invite.")) {
         console.log("hello");
        toast.success("You are already registered.");
//         setTimeout(() => navigate("/evaluator/login"), {
//    state: { toastMessage: "You are already registered. Please login." },
// },4000);
      } else {
        toast.error(msg || "Registration failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: "600px" }}>
      <h2 className="text-center mb-4 fw-bold text-primary">Evaluator Register</h2>
      <form onSubmit={handleRegister}>
        <div className="mb-3">
          <label className="form-label fw-semibold">Name:</label>
          <input
            type="text"
            className="form-control bg-light"
            placeholder="Enter your name"
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          />
        </div>
        <div className="mb-3">
          <label className="form-label fw-semibold">Password:</label>
          <input
            type="password"
            className="form-control bg-light"
            placeholder="Enter your password"
            required
            value={form.password}
            onChange={(e) =>
              setForm((f) => ({ ...f, password: e.target.value }))
            }
          />
        </div>
        <div className="d-grid mt-4">
          <button
            className="btn btn-primary"
            type="submit"
            disabled={loading}
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </div>
      </form>

      <div className="text-center mt-4">
        <p className="fw-semibold text-muted">
          Already registered?{" "}
          <a
            href="http://localhost:3000/evaluator/login"
            className="fw-bold text-primary text-decoration-none"
          >
            Login here
          </a>
        </p>
      </div>
    </div>
  );
};

export default EvaluatorInvite;
