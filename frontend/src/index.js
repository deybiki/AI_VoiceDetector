import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ToastContainer } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';
import ReactDOM from 'react-dom/client';
import './index.css';
import HomePage from './landing_page/home/HomePage';
import Prof_dash from './landing_page/prof_dash/Prof_dash';
import Stud_dash from './landing_page/stud_dash/Stud_Dash';
import Prof_SignUp from './landing_page/signup/Prof-Signup';
import Prof_Login from './landing_page/signup/Prof-Login';
import Stud_Login from './landing_page/signup/Stud-Login';
import Stud_SignUp from './landing_page/signup/Stud-Signup';
import Navbar from './landing_page/Navbar';
import ViewTest from './landing_page/prof_dash/view_tests/ViewTest';
import TestDetails from './landing_page/prof_dash/view_test/TestDetails';
import EvaluatorInvite from './landing_page/evaluator/EvaluatorInvite';
import EvaluatorLogin from './landing_page/evaluator/EvaluatorLogin';
import EvaluatorDashboard from './landing_page/evaluator/EvaluatorDashboard';
import EvaluatorTestAttempts from './landing_page/evaluator/EvaluatorTestAttempts';
import EvaluatorReviewAttempt from './landing_page/evaluator/EvaluatorReview';
import EvaluatorForgotPassword from './landing_page/evaluator/forgot-password/EvaluatorForgotPassword';
import EvaluatorAssignmentAccept from './landing_page/evaluator/EvaluatorAssignmentAccept';


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
   <BrowserRouter>
      <Navbar />
      <Routes>
         <Route path='/' element={<HomePage />} />
         <Route path='/prof-signup' element={<Prof_SignUp />} />
         <Route path='/stud-signup' element={<Stud_SignUp />} />
         <Route path="/prof-dash/:profName" element={<Prof_dash />} />

         <Route path='/stud-dash/:studName' element={<Stud_dash />} />
         <Route path='/prof-login' element={<Prof_Login />} />
         <Route path='/stud-login' element={<Stud_Login />} />

         <Route path="/prof-dash/:profName/view-tests" element={<ViewTest />} />
         <Route path="/prof-dash/:profName/test/:testId" element={<TestDetails />} />

         <Route path="/evaluator/invite" element={<EvaluatorInvite />} />
         <Route path="/evaluator/login" element={<EvaluatorLogin />} />
         <Route path="/evaluator/dashboard" element={<EvaluatorDashboard />} />
         <Route path="/evaluator/test/:testId/attempts" element={<EvaluatorTestAttempts />} />
         <Route path="/evaluator/review/:attemptId" element={<EvaluatorReviewAttempt />} />

         <Route path="/evaluator/forgot-password" element={<EvaluatorForgotPassword />} />
         <Route path="/evaluator/accept" element={<EvaluatorAssignmentAccept />} />


      </Routes>
      <ToastContainer position="top-right" autoClose={3000} />
   </BrowserRouter>
);

