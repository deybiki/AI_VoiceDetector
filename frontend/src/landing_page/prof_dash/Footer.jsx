import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { motion } from "framer-motion";
import Select from "react-select";
import CreatableSelect from "react-select/creatable";
import { useNavigate } from "react-router-dom";

const TestFormSection = () => {
  //const { profName } = useParams();
  // const username = localStorage.getItem("username");

  const navigate = useNavigate();

  // const displayName = username
  //    .split("-")
  //    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
  //    .join(" ");
  const username = localStorage.getItem("username") || "";
  const displayName = username
    ? username
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    : "Professor";

  const [showForm, setShowForm] = useState(false);
  const [studentOptions, setStudentOptions] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [departments, setdepartments] = useState([
    "Computer Science",
    "Electronics",
    "Mechanical",
    "Civil",
    "Instrumentation",
    "Electrical",
  ]); // aap backend se bhi fetch kar sakte ho
  const [selecteddepartment, setSelecteddepartment] = useState("");

  // const [evaluatorOptions, setEvaluatorOptions] = useState([]);
  const [evaluators, setEvaluators] = useState([]);
  const [file, setFile] = useState(null);
  const [formData, setFormData] = useState({
    professorName: displayName,
    description: "",
    testTitle: "",
    startTime: "",
    endTime: "",
    numberOfQuestions: 1,
    questions: [""],
    department: "",
  });

  // Fetch student emails
  useEffect(() => {
    const fetchScholarIds = async () => {
      try {
        const res = await axios.get(
          "http://localhost:5000/api/details/allStudentScholarId",
          { withCredentials: true }
        );
        const options = res.data.scholarIds.map((scholarId) => ({
          label: scholarId,
          value: scholarId,
        }));
        setStudentOptions(options);
      } catch (err) {
        console.log(err);
        toast.error("Failed to load student footer scholar ids");
      }
    };
   
  }, []);

  const fetchScholarIdsByBranch = async (department) => {
    try {
      const res = await axios.get(
        `http://localhost:5000/api/details/studentsByBranch/${department}`,
        { withCredentials: true }
      );
      const options = res.data.scholarIds.map((scholarId) => ({
        label: scholarId,
        value: scholarId,
      }));
      setStudentOptions(options);
    } catch (err) {
      console.log(err);
      toast.error("Failed to load scholar IDs for this branch");
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleQuestionChange = (index, value) => {
    const updated = [...formData.questions];
    updated[index] = value;
    setFormData({ ...formData, questions: updated });
  };

  const handleNumQuestionsChange = (e) => {
    const num = parseInt(e.target.value);
    const updatedQuestions = Array(num).fill("");
    setFormData({
      ...formData,
      numberOfQuestions: num,
      questions: updatedQuestions,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.error("Please upload an Excel file with questions and answers");
      return;
    }
    try {
      const schIds = selectedStudents.map((s) => s.value);

      const testPayload = {
        title: formData.testTitle,
        description: formData.description,
        department: formData.department,
        start_time: formData.startTime,
        end_time: formData.endTime,
        scholarIds: schIds,
      };

      const createTestRes = await axios.post(
        "http://localhost:5000/api/test/create",
        testPayload,
        { withCredentials: true }
      );

      const { test } = createTestRes.data;
      const testId = test._id;

      // Upload Excel sheet for questions + answers
      const formDataExcel = new FormData();
      formDataExcel.append("file", file);

      await axios.post(
        `http://localhost:5000/api/test/${testId}/questions`,
        formDataExcel,
        {
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        }
      );

      // const questionPayload = {
      //    testId,
      //    questions: formData.questions,
      // };

      // await axios.post(
      //    `http://localhost:5000/api/test/${testId}/questions`,
      //    questionPayload,
      //    { withCredentials: true }
      // );

      const evaluatorEmails = evaluators.map((e) => e.value).filter(Boolean);

      if (evaluatorEmails.length > 0) {
        await axios.post(
          `http://localhost:5000/api/examiner/invite-evaluator/${testId}`,
          { evaluatorEmails },
          { withCredentials: true }
        );
      }

      // Reset everything
      setFormData({
        professorName: displayName,
        testTitle: "",
        startTime: "",
        endTime: "",
        numberOfQuestions: 1,
        questions: [""],
        department: "",
      });
      setSelectedStudents([]);
      setEvaluators([]);
      toast.success("Test created and evaluator(s) invited.");
    } catch (err) {
      const errorMsg = err?.response?.data?.msg || "Something went wrong";
      toast.error(errorMsg);
    }
  };

  return (
    <div className="container mt-5">
      <ToastContainer />
      {/* === Animated Cards Section === */}
      <div className="d-flex flex-column flex-md-row justify-content-center align-items-center gap-4 mb-4">
        {/* VIEW PAST TESTS CARD */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-light border border-primary rounded-4 shadow p-4 text-center"
          style={{ width: "700px" }}
        >
          <h5 className="fw-bold text-primary">View Past Tests</h5>
          <p className="text-secondary mb-3">
            Access your previously created tests with complete details — see
            enrolled students, add or remove them, and manage the test
            questions.
          </p>
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ repeat: Infinity, duration: 1 }}
            className="text-primary fs-3"
          >
            ↓
          </motion.div>
        </motion.div>

        {/* CREATE TEST CARD */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-light border border-primary rounded-4 shadow p-4 text-center"
          style={{ width: "700px" }}
        >
          <h5 className="fw-bold text-primary">Create a Test</h5>
          <p className="text-secondary mb-3">
            Start creating a new test — set the title, choose students, define
            test timing, add questions, and optionally assign a human evaluator
            for manual evaluation.
          </p>
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ repeat: Infinity, duration: 1 }}
            className="text-primary fs-3"
          >
            ↓
          </motion.div>
        </motion.div>
      </div>

      {/* === Action Buttons === */}
      <div className="d-flex justify-content-center align-items-center mb-4">
        <button
          className="btn text-white px-4 py-3 shadow me-4"
          style={{
            width: "220px",
            backgroundColor: "#3399ff",
            border: "none",
            fontWeight: "bold",
          }}
          onClick={() => navigate(`/prof-dash/${username}/view-tests`)}
          type="button"
        >
          View Tests
        </button>
        <button
          onClick={() => setShowForm(true)}
          className="btn text-white px-4 py-3 shadow ms-4"
          style={{
            width: "220px",
            backgroundColor: "#3399ff",
            border: "none",
            fontWeight: "bold",
          }}
          type="button"
        >
          Create Test
        </button>
      </div>

      {showForm && (
        <div
          className="card shadow p-5 hover-scale-wrapper"
          style={{
            maxWidth: "1240px",
            margin: "auto",
            transition: "transform 0.3s ease",
            borderRadius: "20px",
          }}
        >
          <div className="d-flex justify-content-between align-items-start flex-wrap">
            <div style={{ flex: "1 1 60%" }}>
              <h3 className="fw-bold mb-3 text-primary">Create Test</h3>

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">Professor Name</label>
                  <input
                    type="text"
                    value={formData.professorName}
                    disabled
                    className="form-control bg-light"
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Department</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={formData.department}
                    onChange={(e) =>
                      setFormData({ ...formData, department: e.target.value })
                    }
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Test Title</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={formData.testTitle}
                    onChange={(e) =>
                      setFormData({ ...formData, testTitle: e.target.value })
                    }
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Test Description</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                  />
                </div>

                <div className="row mb-3">
                  <div className="col">
                    <label className="form-label">Start Time</label>
                    <input
                      type="datetime-local"
                      required
                      className="form-control"
                      value={formData.startTime}
                      onChange={(e) =>
                        setFormData({ ...formData, startTime: e.target.value })
                      }
                    />
                  </div>
                  <div className="col">
                    <label className="form-label">End Time</label>
                    <input
                      type="datetime-local"
                      required
                      className="form-control"
                      value={formData.endTime}
                      onChange={(e) =>
                        setFormData({ ...formData, endTime: e.target.value })
                      }
                    />
                  </div>
                </div>
            {/* select students by branch */}
                <div className="mb-3">
                  <label className="form-label">Select Branch</label>
                  <Select
                    options={departments.map((b) => ({ label: b, value: b }))}
                    value={
                      selecteddepartment
                        ? { label: selecteddepartment, value: selecteddepartment }
                        : null
                    }
                    onChange={(department) => {
                      setSelecteddepartment(department.value);
                      fetchScholarIdsByBranch(department.value);
                    }}
                    placeholder="Choose a branch..."
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">
                    Select Students (from branch)
                  </label>
                  <Select
                    options={studentOptions}
                    isMulti
                    value={selectedStudents}
                    onChange={(selected) => setSelectedStudents(selected)}
                    placeholder="Choose students..."
                  />
                </div>

                {/* <div className="mb-3">
                           <label className="form-label">Number of Questions</label>
                           <input
                              type="number"
                              min="1"
                              required
                              className="form-control"
                              value={formData.numberOfQuestions}
                              onChange={handleNumQuestionsChange}
                           />
                        </div>

                        {formData.questions.map((q, idx) => (
                           <div className="mb-3" key={idx}>
                              <label className="form-label">Question {idx + 1}</label>
                              <input
                                 type="text"
                                 required
                                 className="form-control"
                                 value={q}
                                 onChange={(e) =>
                                    handleQuestionChange(idx, e.target.value)
                                 }
                              />
                           </div>
                        ))} */}

                {/* File Upload for Excel */}
                <div className="mb-3">
                  <label className="form-label">Upload Questions Excel</label>
                  <input
                    type="file"
                    accept=".xlsx, .xls .csv"
                    className="form-control"
                    onChange={handleFileChange}
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Add evaluator(s)</label>
                  <CreatableSelect
                    isMulti
                    placeholder="Type or choose evaluator email(s)..."
                    value={evaluators}
                    onChange={setEvaluators}
                  />
                </div>

                <div className="d-flex justify-content-between mt-4">
                  <button type="submit" className="btn btn-success px-4">
                    Submit
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="btn btn-danger px-4"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>

            <div
              style={{
                flex: "1 1 35%",
                textAlign: "center",
                paddingTop: "20px",
              }}
            >
              <img
                src="https://cdn-icons-png.flaticon.com/512/2221/2221190.png"
                alt="Test Illustration"
                style={{ maxWidth: "150px", marginBottom: "20px" }}
              />
              <p className="text-secondary" style={{ fontSize: "0.95rem" }}>
                Use this form to assign tests to students with full control over
                time and questions.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestFormSection;
