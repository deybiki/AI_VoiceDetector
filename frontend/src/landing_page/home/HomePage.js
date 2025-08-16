import React from "react";
import Hero from "./Hero";
import Upload from "./Upload";
import Cases from "./Cases";
import Usage from "./Usage";
import Navbar from "../Navbar";
import Footer from "../Footer";


function HomePage() {
  return (
    <>
      <Hero />
      <Upload />
      <Usage />
      <Cases />
      {/* <Footer /> */}
    </>
  );
}

export default HomePage;
