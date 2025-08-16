import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "react-toastify";


const EvaluatorReviewAttempt = () => {
   const { attemptId } = useParams();
   const [attempt, setAttempt] = useState(null)

   useEffect(() => {
      axios.get(`http://localhost:5000/api/evaluator/test-attempt/${attemptId}`, { withCredentials: true })
         .then(res => setAttempt(res.data.attempt))
         .catch(() => toast.error("Could not fetch attempt"));
   }, [attemptId])

   const handleReview = async (questionId, rating, review) => {
      try {
         await axios.post(
            `/api/evaluator/review/${attemptId}/${questionId}`,
            { rating, review },
            { withCredentials: true }
         );
         toast.success("Review submitted!");
         // Optionally refresh answer list here
      } catch {
         toast.error("Failed to submit review");
      }
   };


   if (!attempt) return <div>Loading...</div>;

   return (
      <div className="container mt-4">
         <h3>Reviewing: {attempt.student.user?.name}</h3>
         {attempt.answers.map(ans => (
            <div key={ans.question}>
               <div>
                  <strong>Q:</strong> {ans.question.questionText}
               </div>
               <div>
                  <strong>Answer:</strong> {ans.answerText}
               </div>
               <div>
                  <input type="number" min={1} max={5} placeholder="Rating" id={`rating-${ans.question._id}`} />
                  <input type="text" placeholder="Feedback" id={`review-${ans.question._id}`} />
                  <button onClick={() => {
                     const rating = Number(document.getElementById(`rating-${ans.question._id}`).value);
                     const review = document.getElementById(`review-${ans.question._id}`).value;
                     handleReview(ans.question._id, rating, review);
                  }}>Submit Review</button>
               </div>
            </div>
         ))}
      </div>
   )
}

export default EvaluatorReviewAttempt
