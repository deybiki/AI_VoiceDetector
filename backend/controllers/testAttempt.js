import Test from "../models/Test.js";
import Student from "../models/Student.js";
import TestAttempt from "../models/TestAttempt.js";

export const findTestAttempt = async (req, res) => {
  try {
    const { studentId, testId } = req.params;
    console.log("studentId and tesId resp",studentId ,testId);
    // dhyan do: schema me "student" aur "test" field name hain
    const attempt = await TestAttempt.findOne({
      student: studentId,
      test: testId,
    });
    console.log("studentId and tesId resp",studentId ,testId);
    if (!attempt) return res.status(404).json(null);

    res.json(attempt);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// POST /api/testAttempts/:id/submit
export const submitTestAttempt = async (req, res) => {
  try {
    const { studentId, testId } = req.params;
    console.log("submitTestAttempt called");

    const attempt = await TestAttempt.findOneAndUpdate(
      { student: studentId, test: testId }, // query
      { status: "attempted" },             // update
      { new: true }                        // return updated doc
    );

    if (!attempt) {
      return res.status(404).json({ message: "Attempt not found" });
    }

    res.json(attempt);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};



