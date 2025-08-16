import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";

const EvaluatorTestAttempts = () => {
   const { testId } = useParams();
   const [attempts, setAttempts] = useState([]);
   const navigate = useNavigate();

   useEffect(() => {
      axios.get(`http://localhost:5000/api/evaluator/test/${testId}/attempts`, { withCredentials: true })
         .then(res => setAttempts(res.data.attemptedTests))
         .catch(() => toast.error("Could not fetch attempts"));
   }, [testId]);

   return (
      <div className="container mt-4">
         <h3>Student Attempts</h3>
         {attempts.length === 0 && <div>No submissions yet.</div>}
         <ul className="list-group">
            {attempts.map(attempt => (
               <li key={attempt._id} className="list-group-item d-flex justify-content-between">
                  <span>{attempt.student.user?.name} ({attempt.student.scholarId})</span>
                  <button className="btn btn-sm btn-outline-info"
                     onClick={() => navigate(`/evaluator/review/${attempt._id}`)}
                  >Review Answers</button>
               </li>
            ))}
         </ul>
      </div>
   );
};

export default EvaluatorTestAttempts;
