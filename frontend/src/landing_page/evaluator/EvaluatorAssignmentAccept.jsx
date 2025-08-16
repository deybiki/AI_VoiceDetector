import { useEffect, useState } from "react";
import axios from "axios";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const EvaluatorAssignmentAccept = () => {
   const [params] = useSearchParams();
   const testId = params.get("testId");
   const token = params.get("token");
   const [loading, setLoading] = useState(true);
   const navigate = useNavigate();

   useEffect(() => {
      const acceptAssignment = async () => {
         try {
            await axios.get(
               `http://localhost:5000/api/evaluator/accept?testId=${testId}&token=${token}`,
               { withCredentials: true }
            );
            toast.success("You have been added as an evaluator!");
            setTimeout(() => navigate("/evaluator/dashboard"), 1200);
         } catch (err) {
            toast.error(err?.response?.data?.msg || "Failed to accept assignment");
            setTimeout(() => navigate("/evaluator/login"), 1200);
         } finally {
            setLoading(false);
         }
      };
      acceptAssignment();
      // eslint-disable-next-line
   }, []);

   return (
      <div className="container mt-5" style={{ maxWidth: "400px" }}>
         <h3 className="text-center text-primary mb-4">
            {loading ? "Accepting Assignment..." : "Assignment Status"}
         </h3>
         {loading && <div className="text-center">Please wait...</div>}
      </div>
   );
};

export default EvaluatorAssignmentAccept;
