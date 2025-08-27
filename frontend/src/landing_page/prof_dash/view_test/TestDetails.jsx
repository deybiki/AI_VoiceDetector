import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Select from "react-select";
import CreatableSelect from "react-select/creatable";
import Hero from "../Hero";

const TestDetails = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const username = localStorage.getItem("username");
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [studentOptions, setStudentOptions] = useState([]);
  const [departments, setdepartments] = useState([
    "Computer Science",
    "Electronics",
    "Mechanical",
    "Civil",
    "Instrumentation",
    "Electrical",
  ]); // aap backend se bhi fetch kar sakte ho
  const [selecteddepartment, setSelecteddepartment] = useState("");

  // ScholarId select
  const [scholarOptions, setScholarOptions] = useState([]);
  const [selectedScholar, setSelectedScholar] = useState(null);
  const [addQuestionText, setAddQuestionText] = useState("");

  // For evaluator invites (free entry)
  const [evaluators, setEvaluators] = useState([]);
  const [file, setFile] = useState(null);

  // Fetch branches (example API)
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

  // Fetch scholar IDs based on selected branch
  const fetchScholarOptions = async (branch) => {
    if (!branch) return;
    try {
      const res = await axios.get(
        `http://localhost:5000/api/details/unaddedScholarId/${testId}?branch=${branch}`,
        { withCredentials: true }
      );
      setScholarOptions(
        res.data.scholarIds.map((sid) => ({
          value: sid,
          label: sid,
        }))
      );
    } catch {
      toast.error("Failed to fetch scholar IDs");
    }
  };

  // Fetch test details
  const fetchTest = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:5000/api/test/${testId}`, {
        withCredentials: true,
      });
      setTest(res.data.test);
    } catch (err) {
      toast.error("Failed to fetch test details");
    } finally {
      setLoading(false);
    }
  };
  //for upload file
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.warn("Please upload a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(
        `http://localhost:5000/api/test/${testId}/questions`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        }
      );
      toast.success("Questions uploaded successfully!");
      setFile(null);
      fetchTest();
    } catch (err) {
      toast.error(err?.response?.data?.msg || "Upload failed");
    }
  };

  // Get all existing evaluator emails (assigned only)
  const getAlreadyInvitedEmails = () => {
    const assigned = (test?.evaluators || []).map((e) =>
      e.email?.toLowerCase()
    );
    return new Set([...assigned]);
  };

  // Add evaluator(s) via invite, but only if not already invited
  const addEvaluator = async () => {
    setLoading(true);
    try {
      const allExisting = getAlreadyInvitedEmails();
      const evaluatorEmails = evaluators
        .map((e) => e.value.trim().toLowerCase())
        .filter((email) => !!email && !allExisting.has(email));

      if (evaluatorEmails.length === 0) {
        toast.warn("All these evaluators are already invited or assigned.");
        setLoading(false);
        return;
      }

      await axios.post(
        `http://localhost:5000/api/examiner/invite-evaluator/${testId}`,
        { evaluatorEmails },
        { withCredentials: true }
      );
      toast.success("Invitations sent!");
      setEvaluators([]);
      fetchTest();
    } catch (err) {
      toast.error(err?.response?.data?.msg || "Failed to add evaluators");
    } finally {
      setLoading(false);
    }
  };

  // Fetch available scholar IDs
  //   const fetchScholarOptions = async () => {
  //     try {
  //       const res = await axios.get(
  //         `http://localhost:5000/api/details/unaddedScholarId/${testId}`,
  //         { withCredentials: true }
  //       );
  //       setScholarOptions(
  //         res.data.scholarIds.map((sid) => ({
  //           value: sid,
  //           label: sid,
  //         }))
  //       );
  //     } catch {
  //       toast.error("Failed to fetch scholar IDs");
  //     }
  //   };

  useEffect(() => {
    fetchTest();
    fetchScholarOptions();
    // eslint-disable-next-line
  }, [testId]);

  // Remove Test
  const removeTest = async (id) => {
    if (!window.confirm("Are you sure you want to delete this test?")) return;
    try {
      await axios.delete(
        `http://localhost:5000/api/examiner/remove/test/${id}`,
        { withCredentials: true }
      );
      toast.success("Test deleted");
      navigate(`/prof-dash/${username}/view-tests`);
    } catch (error) {
      toast.error("Failed to remove test");
    }
  };

  // Remove Student
  const handleRemoveStudent = async (studentId) => {
    try {
      await axios.delete(
        `http://localhost:5000/api/examiner/remove/${test._id}/student/${studentId}`,
        { withCredentials: true }
      );
      toast.success("Student removed");
      fetchTest();
      fetchScholarOptions();
    } catch {
      toast.error("Failed to remove student");
    }
  };

  // Add Student
  //   const handleAddStudent = async () => {
  //     if (!selectedScholar) {
  //       toast.warn("Choose a Scholar ID");
  //       return;
  //     }
  //     try {
  //       await axios.post(
  //         `http://localhost:5000/api/examiner/invite/${test._id}`,
  //         { scholarIds: [selectedScholar.value] },
  //         { withCredentials: true }
  //       );
  //       toast.success("Student added");
  //       setSelectedScholar(null);
  //       fetchTest();
  //       fetchScholarOptions();
  //     } catch (err) {
  //       toast.error(err?.response?.data?.msg || "Failed to add student");
  //     }
  //   };

  // Multiple students add karne ka function
  // Add Students (multiple)
  const handleAddStudents = async () => {
    if (!selectedStudents || selectedStudents.length === 0) {
      toast.warn("Choose at least one Scholar ID");
      return;
    }

    try {
      const scholarIds = selectedStudents.map((s) => s.value);

      await axios.post(
        `http://localhost:5000/api/examiner/invite/${test._id}`,
        { scholarIds },
        { withCredentials: true }
      );

      toast.success("Students added successfully");
      setSelectedStudents([]);
      fetchTest();
      fetchScholarOptions(selecteddepartment);
    } catch (err) {
      toast.error(err?.response?.data?.msg || "Failed to add students");
    }
  };

  // Remove Question
  const handleRemoveQuestion = async (questionId) => {
    try {
      await axios.delete(
        `http://localhost:5000/api/test/${test._id}/question/${questionId}`,
        { withCredentials: true }
      );
      toast.success("Question removed");
      fetchTest();
    } catch {
      toast.error("Failed to remove question");
    }
  };

  // Add Question
  const handleAddQuestion = async () => {
    if (!addQuestionText.trim()) {
      toast.warn("Enter a question");
      return;
    }
    try {
      await axios.post(
        `http://localhost:5000/api/test/${test._id}/question`,
        { question: addQuestionText },
        { withCredentials: true }
      );
      toast.success("Question added");
      setAddQuestionText("");
      fetchTest();
    } catch {
      toast.error("Failed to add question");
    }
  };

  // Used for CreatableSelect: block creating an option for already invited
  const isValidNewOption = (inputValue) => {
    if (!inputValue) return false;
    const allExisting = getAlreadyInvitedEmails();
    return !allExisting.has(inputValue.trim().toLowerCase());
  };

  if (loading)
    return (
      <div className="text-center mt-5">
        <div className="spinner-border text-primary" role="status"></div>
        <div>Loading test details...</div>
      </div>
    );

  if (!test)
    return (
      <div className="container py-4">
        <ToastContainer />
        <div className="alert alert-danger text-center">
          Test not found or failed to load.
        </div>
      </div>
    );

  // Assigned evaluators
  const assignedList = test.evaluators || [];

  return (
    <>
      <Hero />
      <ToastContainer />
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2
            className="fw-bold"
            style={{ fontSize: "2.2rem", color: "#0d0d0d" }}
          >
            Test Details
          </h2>
          <div>
            <button
              className="btn btn-outline-danger px-4 me-2"
              onClick={() => removeTest(test._id)}
            >
              Delete Test
            </button>
            <button
              className="btn btn-outline-primary px-4"
              onClick={() => navigate(`/prof-dash/${username}/view-tests`)}
            >
              Back to All Tests
            </button>
          </div>
        </div>

        <div
          className="card shadow-lg mb-4 border-0"
          style={{ borderRadius: "14px", backgroundColor: "#e6f4ff" }}
        >
          <div className="card-body">
            <h4 className="card-title fw-semibold text-primary mb-3">
              {test.title}
            </h4>
            <div style={{ fontSize: "1.05rem" }}>
              <p>
                <strong>Department:</strong> {test.department || "N/A"}
              </p>
              <p>
                <strong>Start:</strong>{" "}
                {new Date(test.start_time).toLocaleString("en-IN", {
                  timeZone: "Asia/Kolkata",
                })}
              </p>
              <p>
                <strong>End:</strong>{" "}
                {new Date(test.end_time).toLocaleString("en-IN", {
                  timeZone: "Asia/Kolkata",
                })}
              </p>
              <p>
                <strong>Test Link:</strong>
                <br />
                <span className="text-primary small">
                  {test.sharedLinkId
                    ? `${window.location.origin}/test/${test.sharedLinkId}`
                    : "-"}
                </span>
              </p>
              <p>
                <strong>No. of Questions:</strong> {test.questions?.length ?? 0}
              </p>
              <p>
                <strong>No. of Students:</strong> {test.students?.length ?? 0}
              </p>
            </div>
          </div>
        </div>
        {new Date(test.start_time) > new Date() && (
          <div className="row">
            {/* Questions */}
            <div className="col-md-6 mb-4">
              <div
                className="card h-100 shadow-sm border-0"
                style={{ borderRadius: "12px", backgroundColor: "#e6f4ff" }}
              >
                <div className="card-header bg-primary text-white fw-bold d-flex justify-content-between align-items-center">
                  Questions
                  <span className="badge bg-light text-primary">
                    {test.questions?.length ?? 0}
                  </span>
                </div>
                <ul className="list-group list-group-flush">
                  {(test.questions || []).length === 0 ? (
                    <li className="list-group-item text-muted">
                      No questions found.
                    </li>
                  ) : (
                    test.questions.map((q, idx) => (
                      <li
                        key={q._id || idx}
                        className="list-group-item d-flex justify-content-between align-items-center"
                      >
                        <span>
                          <strong>Q{idx + 1}:</strong>{" "}
                          {q.questionText || "Untitled"}
                        </span>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleRemoveQuestion(q._id)}
                        >
                          Remove
                        </button>
                      </li>
                    ))
                  )}
                </ul>
                <div className="p-3 border-top">
                  <form onSubmit={handleUpload}>
                    <div className="d-flex align-items-center gap-2">
                      <input
                        type="file"
                        accept=".csv,.xlsx"
                        className="form-control"
                        onChange={(e) => setFile(e.target.files[0])}
                      />
                      <button className="btn btn-primary" type="submit">
                        Upload
                      </button>
                    </div>
                    <small className="text-muted">
                      Upload a CSV/XLSX file with headers: <b>questionText</b>{" "}
                      and <b>answerText</b>
                    </small>
                  </form>
                </div>
              </div>
            </div>

            {/* Students */}
            <div className="col-md-6 mb-4">
              <div
                className="card h-100 shadow-sm border-0"
                style={{ borderRadius: "12px", backgroundColor: "#e6f4ff" }}
              >
                <div className="card-header bg-primary text-white fw-bold d-flex justify-content-between align-items-center">
                  Students
                  <span className="badge bg-light text-success">
                    {test.students?.length ?? 0}
                  </span>
                </div>
                <ul className="list-group list-group-flush">
                  {(test.students || []).length === 0 ? (
                    <li className="list-group-item text-muted">
                      No students invited.
                    </li>
                  ) : (
                    test.students.map((s, idx) => (
                      <li
                        key={s._id || idx}
                        className="list-group-item d-flex justify-content-between align-items-center"
                      >
                        <span>
                          <strong>{s.scholarId}</strong> —{" "}
                          {s.user?.name || "Unknown"} (
                          {s.user?.email || "No email"})
                        </span>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleRemoveStudent(s._id)}
                        >
                          Remove
                        </button>
                      </li>
                    ))
                  )}
                </ul>
                {/* select students by branch */}
                <div className="mb-3">
                  <label className="form-label">Select Branch</label>
                  <Select
                    options={departments.map((b) => ({ label: b, value: b }))}
                    value={
                      selecteddepartment
                        ? {
                            label: selecteddepartment,
                            value: selecteddepartment,
                          }
                        : null
                    }
                    onChange={(department) => {
                      setSelecteddepartment(department.value);
                      fetchScholarIdsByBranch(department.value);
                    }}
                    placeholder="Choose a branch..."
                  />
                </div>

                {/* Select Students */}
                <div className="mb-3">
                  <label className="form-label fw-semibold">
                    Select Students
                  </label>
                  <Select
                    options={[
                      { value: "all", label: "Select All" },
                      ...studentOptions,
                    ]}
                    isMulti
                    value={selectedStudents}
                    onChange={(selected) => {
                      if (!selected) {
                        setSelectedStudents([]);
                        return;
                      }

                      const isSelectAll = selected.find(
                        (s) => s.value === "all"
                      );

                      if (isSelectAll) {
                        // Merge all students from current branch + already selected
                        const merged = [
                          ...selectedStudents,
                          ...studentOptions.filter(
                            (opt) =>
                              !selectedStudents.some(
                                (s) => s.value === opt.value
                              )
                          ),
                        ];
                        setSelectedStudents(merged);
                      } else {
                        // Merge normal selection with already selected students
                        const merged = [
                          ...selectedStudents.filter((s) =>
                            studentOptions.some((opt) => opt.value === s.value)
                          ), // remove duplicates from same branch
                          ...selected,
                        ];
                        setSelectedStudents(merged);
                      }
                    }}
                    placeholder="Choose students..."
                  />
                </div>
                <button
                  className="btn btn-primary w-100"
                  onClick={handleAddStudents}
                >
                  Add Selected Students
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Evaluators Section */}
        {new Date(test.start_time) > new Date() && (
          <div className="row">
            <div className="col-md-12 mb-4">
              <div
                className="card h-100 shadow-sm border-0"
                style={{ borderRadius: "12px", backgroundColor: "#e6f4ff" }}
              >
                <div className="card-header bg-primary text-white fw-bold d-flex justify-content-between align-items-center">
                  Evaluators
                  <span className="badge bg-light text-dark">
                    {assignedList.length}
                  </span>
                </div>
                <div className="mb-2">
                  <strong>Assigned Evaluators:</strong>
                  <ul className="list-group list-group-flush">
                    {assignedList.length === 0 ? (
                      <li className="list-group-item text-muted">None</li>
                    ) : (
                      assignedList.map((e, idx) => (
                        <li
                          key={e._id || e.email || idx}
                          className="list-group-item"
                        >
                          {e.email}
                        </li>
                      ))
                    )}
                  </ul>
                </div>
                <div className="card-body border-top">
                  <form
                    className="d-flex gap-2 align-items-center"
                    onSubmit={async (e) => {
                      e.preventDefault();
                      await addEvaluator();
                    }}
                  >
                    <CreatableSelect
                      isMulti
                      value={evaluators}
                      onChange={setEvaluators}
                      placeholder="Type evaluator emails and press Enter"
                      formatCreateLabel={(inputValue) => `Add "${inputValue}"`}
                      isValidNewOption={isValidNewOption}
                    />
                    <button
                      className="btn btn-primary"
                      type="submit"
                      disabled={evaluators.length === 0}
                    >
                      Invite
                    </button>
                  </form>
                  <small className="text-muted d-block mt-2">
                    Add multiple evaluator emails by typing and pressing Enter.
                  </small>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default TestDetails;
