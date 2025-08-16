import User from "../models/User.js";
import Student from "../models/Student.js";
import Test from "../models/Test.js";

export const getAllStudentEmails = async (req, res) => {
   try {
      const students = await User.find({ role: "student" }).select("email");

      res.json({ emails: students.map(s => s.email) });
   } catch {
      res.status(500).json({ msg: "Failed to fetch student emails" });
   }
};

export const getAllProfEmails = async (req, res) => {
   try {
      const profs = await User.find({ role: "examiner" }).select("email username name");
      res.json({ professors: profs });
   } catch {
      res.status(500).json({ msg: "Failed to fetch prof emails and usernames" });
   }
};

export const getUnaddedStudentScholarId = async (req, res) => {
   try {
      const { testId } = req.params;

      const students = await Student.find({}, "scholarId");

      const test = await Test.findById(testId);

      if (!test) {
         return res.status(404).json({ msg: "Test not found" });
      }

      const testStudentIds = new Set(test.students.map(id => id.toString()));

      const unaddedScholarIds = students
         .filter(s => !testStudentIds.has(s._id.toString()))
         .map(s => s.scholarId);

      res.status(200).json({ scholarIds: unaddedScholarIds });
   } catch (err) {
      console.error("Server error:", err);
      res.status(500).json({ msg: "Server error" });
   }
};


export const getAllStudentScholarId = async (req, res) => {
   try {
      const students = await Student.find()

      const scholarIds = students.map(s => s.scholarId)
      return res.status(200).json({ scholarIds })
   } catch (error) {
      console.error("Server error:", err);
      res.status(500).json({ msg: "Server error" });
   }
}