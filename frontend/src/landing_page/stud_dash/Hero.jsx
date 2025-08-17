// import React, { useEffect } from "react";
// import { useNavigate, useLocation } from "react-router-dom";

// function Hero() {
//   const navigate = useNavigate();
//   const location = useLocation();

//   // Extract the username from the last part of the URL
//   const username = location.pathname.split("/").filter(Boolean).pop();
//   console.log("username:", username);

//   useEffect(() => {
//     const token = localStorage.getItem("token");
//     if (!token) {
//       navigate("/"); // Redirect if not logged in
//     }
//   }, [navigate]);

//   const handleLogout = () => {
//     localStorage.removeItem("token");
//     navigate("/");
//   };

//   return (
//     <div>
//       {/* Custom Navbar */}
//       <div
//         className="d-flex justify-content-between align-items-center px-4 py-3"
//         style={{
//           backgroundColor: "#cce5ff",
//           fontSize: "1.5rem",
//           fontWeight: "500",
//           borderBottom: "2px solid #b8daff",
//         }}
//       >
//         <div className="d-flex align-items-center gap-2">
//           <i
//             className="fa fa-graduation-cap"
//             aria-hidden="true"
//             style={{ fontSize: "2rem", color: "#004085" }}
//           ></i>
//           <span className="text-dark">Welcome  <strong>{username}</strong></span>
//         </div>

//         <button className="btn btn-danger btn-sm px-3 fw-semibold" onClick={handleLogout}>
//           Logout
//         </button>
//       </div>

//       {/* Main Content */}
//       <div className="container mt-4">
//         <div className="row justify-content-center text-center">
//           <img
//             src="/proj_img/gpt4.png"
//             alt="Hero"
//             className="mb-2"
//             style={{ width: "750px", height: "auto" }}
//           />
//         </div>
//       </div>
//     </div>
//   );
// }

// export default Hero;

import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Hero() {
  const navigate = useNavigate();

  const username = localStorage.getItem("username") || "user";
  const image = localStorage.getItem("image");
  const displayName = username
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  useEffect(() => {
    const token = localStorage.getItem("token");

    console.log("Token from localStorage:", token);

    if (!token) {
      navigate("/");
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div>
      {/* Navbar */}
      <div
        className="d-flex justify-content-between align-items-center px-4 py-3"
        style={{
          backgroundColor: "#cce5ff",
          fontSize: "1.5rem",
          fontWeight: "500",
          borderBottom: "2px solid #b8daff",
        }}
      >
        <div className="d-flex align-items-center gap-2">
          <i
            className="fa fa-black-tie"
            aria-hidden="true"
            style={{ fontSize: "2rem" }}
          ></i>
          <span className="text-dark">
            Welcome <strong>{displayName}</strong>
          </span>
        </div>
        <button
          className="btn btn-danger btn-sm px-3 fw-semibold"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>

      {/* Profile + Hero Image Section */}
      <div className="d-flex px-4 my-3">
        {/* Profile Image (Top-Left) */}
        <div className="me-4 align-self-start">
          <img
            src={image}
            alt="Profile"
            style={{
              width: "120px",
              height: "120px",
              borderRadius: "50%",
              objectFit: "cover",
              border: "3px solid #004085",
            }}
          />
        </div>

        {/* Hero Image (Center) */}
        <div className="flex-grow-1 d-flex justify-content-center">
          <img
            src="/proj_img/gpt5.png"
            alt="Hero"
            style={{ maxWidth: "750px", width: "100%", height: "auto" }}
          />
        </div>
      </div>
    </div>
  );
}

export default Hero;
