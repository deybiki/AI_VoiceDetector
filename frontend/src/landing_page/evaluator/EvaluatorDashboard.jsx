import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const EvaluatorDashboard = () => {
   const [tests, setTests] = useState([]);
   const navigate = useNavigate();

   useEffect(() => {
      axios
         .get("http://localhost:5000/api/evaluator/tests", { withCredentials: true })
         .then((res) => setTests(res.data.tests))
         .catch(() => toast.error("Could not fetch assigned tests"));
   }, []);

   const handleDeleteAccount = async () => {
      if (!window.confirm("Are you sure you want to delete your evaluator account? This cannot be undone.")) {
         return;
      }
      try {
         await axios.delete("http://localhost:5000/api/evaluator/me", { withCredentials: true });
         toast.success("Account deleted. Logging out...");
         setTimeout(() => navigate("/evaluator/login"), 1500);
      } catch (err) {
         toast.error("Error deleting account");
      }
   };

   return (
      <div className="container mt-5">
         <div className="card shadow-lg">
            <div className="card-header bg-primary text-white">
               <h3 className="mb-0">Assigned Tests</h3>
            </div>
            <div className="card-body">
               {tests.length === 0 ? (
                  <p className="text-muted">No tests assigned.</p>
               ) : (
                  <ul className="list-group">
                     {tests.map((test) => (
                        <li
                           key={test._id}
                           className="list-group-item d-flex justify-content-between align-items-center"
                        >
                           <span>
                              <strong>{test.title}</strong>{" "}
                              <span className="text-muted">
                                 ({test.department || "N/A"})
                              </span>
                           </span>
                           <button
                              className="btn btn-primary btn-sm"
                              onClick={() => navigate(`/evaluator/test/${test._id}/attempts`)}
                           >
                              Review Submissions
                           </button>
                        </li>
                     ))}
                  </ul>
               )}
            </div>
         </div>
         {/* Delete Account Button */}
         <button
            className="btn btn-danger mt-4"
            onClick={handleDeleteAccount}
         >
            Delete My Account
         </button>
      </div>
   );
};

export default EvaluatorDashboard;
