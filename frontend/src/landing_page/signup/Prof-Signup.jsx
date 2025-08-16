import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { motion } from "framer-motion"; // ✅ Import Framer Motion
import "./Prof-Signup.css";

const Prof_Signup = ({ onClose }) => {
  const navigate = useNavigate();
  const [inputValue, setInputValue] = useState({
    name: "",
    email: "",
    password: "",
    username: "",
    department: ""
  });

  const { name, email, password, username, department } = inputValue;

  const handleOnChange = (e) => {
    const { name, value } = e.target;
    setInputValue((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleError = (err) =>
    toast.error(err, {
      position: "bottom-left",
    });

  const handleSuccess = (msg) =>
    toast.success(msg, {
      position: "bottom-right",
    });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        name,
        username,
        email,
        password,
        role: "examiner",
        examinerData: { department }
      };

      const { data } = await axios.post(
        "http://localhost:5000/api/auth/register",
        payload,
        { withCredentials: true }
      );

      handleSuccess(data.msg);
      setTimeout(() => {
        const profName = username.replace(/\s+/g, '-').toLowerCase();
        navigate(`/prof-dash/${profName}`);
      }, 1000);
    } catch (error) {
      console.error("SIGNUP ERROR:", error);
      if (error.response?.data?.msg) {
        handleError(error.response.data.msg);
      } else {
        handleError("Something went wrong!");
      }
    }

    setInputValue({
      name: "",
      email: "",
      password: "",
      username: "",
      department: ""
    });
  };

  return (
    <motion.div
      className="signup-wrapper"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <h2 className="signup-title">Professor Register</h2>
      <form className="signup-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Name:</label>
          <input
            type="text"
            name="name"
            value={name}
            onChange={handleOnChange}
            placeholder="Enter your name"
            required
          />
        </div>
        <div className="form-group">
          <label>Username:</label>
          <input
            type="text"
            name="username"
            value={username}
            onChange={handleOnChange}
            placeholder="Choose a username"
            required
          />
        </div>
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={email}
            onChange={handleOnChange}
            placeholder="Enter your email"
            required
          />
        </div>
        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={password}
            onChange={handleOnChange}
            placeholder="Enter your password"
            required
          />
        </div>
        <div className="form-group">
          <label>Department:</label>
          <input
            type="text"
            name="department"
            value={department}
            onChange={handleOnChange}
            placeholder="Enter your department"
            required
          />
        </div>
        <div className="form-check">
          <input type="checkbox" id="agree" required />
          <label htmlFor="agree">
            I agree to the AI Voice Detector <a href="/terms">user agreement</a>
          </label>
        </div>
        <button type="submit" className="submit-btn">
          Create an Account
        </button>
        <div className="login-redirect">
          Already have an account? <a href="/prof-login">Login</a>
        </div>
      </form>
      <ToastContainer />
    </motion.div>
  );
};

export default Prof_Signup;
