// import React from "react";
// import { Link } from "react-router-dom";

// function Hero() {
//   return (
//     // <div className='container mt-4'>
//     //     <div className='row justify-content-center'>
//     //         <div className='col-md-8  p-3'>
//     //             <img
//     //                 src='proj_img/unsp1.jpg'
//     //                 alt='Hero image'
//     //                 className='img-fluid rounded shadow'
//     //                 style={{ maxWidth: '100%', height: '500px', objectFit: 'cover' }}
//     //             />
//     //         </div>
//     //     </div>
//     // </div>
//     <div className="container p-5">
//       <div
//         className="row justify-content-center text-center"
//         // justify-content-center centers the flex items horizontally
//       >
//         <img
//           src="proj_img/gpt3.png"
//           alt="Hero image"
//           className="mb-2"
//           style={{ width: "750px", height: "auto" }}
//         />
//         <h1
//           className="mt-5 fw-bold"
//           style={{ fontFamily: "'Playfair Display', serif" }}
//         >
//           Smarter Viva Evaluations with AI
//         </h1>
//         <p>
//           Professors craft personalized, time-bound viva exams while students respond via voice — with instant AI insights revealing answer authenticity and depth.
//         </p>
//         <Link to="/">
//           <button
//             className="p-2 btn btn-primary fs-5"
//             style={{ width: "20%", margin: "0 auto" }}
//             to="/"
//           >
//             Signup Now
//           </button>
//         </Link>
//       </div>
//     </div>
//   );
// }

// export default Hero;






import React from "react";
import { Link } from "react-router-dom";

function Hero() {
  return (
    <div className="container p-5">
      <div className="row justify-content-center text-center">
        <img
          src="proj_img/gpt3.png"
          alt="Hero image"
          className="mb-2"
          style={{ width: "750px", height: "auto" }}
        />
        <h1 className="mt-5 fw-bold" style={{ fontFamily: "'Playfair Display', serif" }}>
          Smarter Viva Evaluations with AI
        </h1>
        <p>
          Professors craft personalized, time-bound viva exams while students respond via voice — with instant AI insights revealing answer authenticity and depth.
        </p>
        <Link to="/">
          <button className="p-2 btn btn-primary fs-5" style={{ width: "20%", margin: "0 auto" }}>
            Signup Now
          </button>
        </Link>
      </div>
    </div>
  );
}

export default Hero;

