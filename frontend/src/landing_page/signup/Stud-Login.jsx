// import React, { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import axios from "axios";
// import { ToastContainer, toast } from "react-toastify";
// import "react-toastify/dist/ReactToastify.css";
// import { motion } from "framer-motion"; // ✅ Import Framer Motion
// import "./Stud-Login.css";

// const Stud_Login = () => {
//   const navigate = useNavigate();
//   const [inputValue, setInputValue] = useState({
//     email: "",
//     password: "",
//   });

//   const { email, password } = inputValue;

//   const handleOnChange = (e) => {
//     const { name, value } = e.target;
//     setInputValue((prev) => ({
//       ...prev,
//       [name]: value,
//     }));
//   };

//   const handleError = (err) => toast.error(err, { position: "bottom-left" });
//   const handleSuccess = (msg) => toast.success(msg, { position: "bottom-right" });



//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       const { data } = await axios.post(
//         "http://localhost:5000/api/auth/login",
//         { email, password },
//         { withCredentials: true }
//       );

//       localStorage.setItem("token", data.token);
//       localStorage.setItem("user", JSON.stringify(data.user));
//       localStorage.setItem("profile", JSON.stringify(data.profile));


//       localStorage.setItem("username", data.profile.scholarId);
//       console.log("Stored scholarId:", data.profile.scholarId);

//       const role = data.user.role;
//       const username = data.user.username?.replace(/\s+/g, "-").toLowerCase();

//       if (role === "student") {
//         handleSuccess("Login Successful");
//       } else {
//         handleError("Login Failed. Try Again.");
//       }

//       setTimeout(() => {
//         if (role === "student") {
//           navigate(`/stud-dash/${username}`);
//         }
//       }, 1000);
//     } catch (error) {
//       console.error("LOGIN ERROR:", error);
//       if (error.response?.data?.msg) {
//         handleError(error.response.data.msg);
//       } else {
//         handleError("Login failed. Try again.");
//       }
//     }

//     setInputValue({
//       email: "",
//       password: "",
//     });
//   };



  
//   return (
//     <motion.div
//       className="signup-wrapper"
//       initial={{ opacity: 0, y: 30 }}
//       animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.5, ease: "easeOut" }}
//     >
//       <h2 className="signup-title">Student Login</h2>
//       <form className="signup-form" onSubmit={handleSubmit}>
//         <div className="form-group">
//           <label>Email:</label>
//           <input
//             type="email"
//             name="email"
//             value={email}
//             onChange={handleOnChange}
//             placeholder="Enter your email"
//             required
//           />
//         </div>
//         <div className="form-group">
//           <label>Password:</label>
//           <input
//             type="password"
//             name="password"
//             value={password}
//             onChange={handleOnChange}
//             placeholder="Enter your password"
//             required
//           />
//         </div>
//         <div className="form-check">
//           <input type="checkbox" id="agree" required />
//           <label htmlFor="agree">
//             I agree to the AI Voice Detector <a href="/terms">user agreement</a>
//           </label>
//         </div>
//         <button type="submit" className="submit-btn">
//           Login
//         </button>
//         <div className="login-redirect">
//           Don’t have an account? <a href="/stud-signup">Register</a>
//         </div>
//       </form>
//       <ToastContainer />
//     </motion.div>
//   );
// };

// export default Stud_Login;










import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "react-toastify"; // 👈 ToastContainer will now move to App.js
import "react-toastify/dist/ReactToastify.css";
import { motion } from "framer-motion";
import "./Stud-Login.css";

const Stud_Login = () => {
  const navigate = useNavigate();
  const [inputValue, setInputValue] = useState({
    email: "",
    password: "",
  });

  const { email, password } = inputValue;

  const handleOnChange = (e) => {
    const { name, value } = e.target;
    setInputValue((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleError = (err) => {
    if (err) {
      toast.error(err, { position: "bottom-left" });
    } else {
      toast.error("Something went wrong", { position: "bottom-left" });
    }
  };

  const handleSuccess = (msg) => {
    if (msg) {
      toast.success(msg, { position: "bottom-right" });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await axios.post(
        "http://localhost:5000/api/auth/login",
        { email, password },
        { withCredentials: true }
      );

      // localStorage.setItem("token", data.token);
      // localStorage.setItem("user", JSON.stringify(data.user));
      // localStorage.setItem("profile", JSON.stringify(data.profile));

      // // ✅ Check if scholarId exists before storing
      // if (data.profile?.scholarId) {
      //   localStorage.setItem("username", data.profile.scholarId);
      //   console.log("Stored scholarId:", data.profile.scholarId);
      // } else {
      //   console.warn("⚠️ scholarId not found in profile data");
      // }

      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      localStorage.setItem("profile", JSON.stringify(data.profile));

// ✅ Use scholarId for the viva system, NOT username
      if (data.profile && data.profile.scholarId && data.profile.image) {
        localStorage.setItem("username", data.profile.scholarId);  
        localStorage.setItem("image",data.profile.image);
        console.log("image link: ",data.profile.image);
        console.log(" Stored scholarId:", data.profile.scholarId);
      } else {
        console.warn("⚠️ scholarId not found in profile data");
      }


      const role = data.user.role;
      const username = data.user.username?.replace(/\s+/g, "-").toLowerCase();

      if (role === "student") {
        handleSuccess("Login Successful");

        setTimeout(() => {
          navigate(`/stud-dash/${username}`);
        }, 1000);
      } else {
        handleError("Login Failed. Not a student.");
      }
    } catch (error) {
      console.error("LOGIN ERROR:", error);
      if (error.response?.data?.msg) {
        handleError(error.response.data.msg);
      } else {
        handleError("Login failed. Please try again.");
      }
    }

    setInputValue({
      email: "",
      password: "",
    });
  };

  return (
    <motion.div
      className="signup-wrapper"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <h2 className="signup-title">Student Login</h2>
      <form className="signup-form" onSubmit={handleSubmit}>
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
        <div className="form-check">
          <input type="checkbox" id="agree" required />
          <label htmlFor="agree">
            I agree to the AI Voice Detector <a href="/terms">user agreement</a>
          </label>
        </div>
        <button type="submit" className="submit-btn">
          Login
        </button>
        <div className="login-redirect">
          Don’t have an account? <a href="/stud-signup">Register</a>
        </div>
      </form>
    </motion.div>
  );
};

export default Stud_Login;
