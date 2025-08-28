import Test from "../models/Test.js";
import Question from "../models/Question.js";
import TestAnswer from "../models/TestAnswer.js";
import TestAttempt from "../models/TestAttempt.js";
import { v4 as uuidv4 } from "uuid";
import Student from "../models/Student.js";
import User from "../models/User.js";
import Examiner from "../models/Examiner.js";
import xlsx from "xlsx";

export const createTest = async (req, res) => {
   try {
      // console.log("req body:",req.body);
      const { title, start_time,description, end_time, department } = req.body;
      let { scholarIds } = req.body;

      const sharedLinkId = uuidv4();

      if (typeof scholarIds === "string") scholarIds = [scholarIds]
      if (!Array.isArray(scholarIds) || !scholarIds.length)
         return res.status(400).json({ msg: "Provide at least one student Id" });


      const students = await Student.find({ scholarId: { $in: scholarIds } }).populate('user');

      const added = students
         .filter(st => st.user && st.user.role === "student")
         .map(st => st._id);

      const examiner = await Examiner.findOne({ user: req.user._id })
      if (!examiner) {
         return res.status(403).json({ msg: "Unauthorized" })
      }
      const examinerId = examiner._id

      const test = await Test.create({
         title,
         examiner: examinerId,
         description,
         department,
         start_time,
         end_time,
         sharedLinkId,
         students: added
      });

      res.status(200).json({ msg: "Test created", test });

   } catch (err) {
      console.error("Error creating test:", err);
      res.status(500).json({ msg: "An error occurred while creating the test" });
   }
};

export const getTest = async (req, res) => {
   try {
      const { testId } = req.params
      const test = await Test.findById(testId)
         .populate({
            path: "students",
            populate: { path: "user", select: "email name" }
         })
         .populate("questions")
         .populate("evaluators", "email");

      if (!test) {
         return res.status(404).json({
            msg: "Test not found"
         })
      }
      return res.status(200).json({
         msg: "Test fetched", test
      })
   } catch (err) {
      console.error("Error fetching test:", err);
      res.status(500).json({ msg: "An error occurred while fetching the test" });
   }
}

export const addQuestion = async (req, res) => {
   try {
      const { testId } = req.params;
      const { question } = req.body;

      const test = await Test.findById(testId);
      if (!test) return res.status(404).json({ msg: "Test not found" });

      const q = await Question.create({ testId, questionText: question });

      test.questions.push(q._id);

      await test.save();

      res.status(200).json({ msg: "Question added successfully" });
   } catch (err) {
      console.error(err);
      res.status(500).json({ msg: "Internal error occurred" });
   }
};

// export const addQuestions = async (req, res) => {
//    try {
//       const { testId } = req.params;
//       const { questions } = req.body;

//       if (!testId || !Array.isArray(questions))
//          return res.status(400).json({ msg: "Invalid testId or questions" });

//       const test = await Test.findById(testId);
//       if (!test) return res.status(404).json({ msg: "Test not found" });

//       const docs = await Promise.all(
//          questions.map(qt => Question.create({ testId, questionText: qt }))
//       );

//       test.questions.push(...docs.map(d => d._id));

//       await test.save();

//       res.status(200).json({ msg: "Questions added successfully" });
//    } catch (err) {
//       console.error("Add questions error:", err);
//       res.status(500).json({ msg: "Server error while adding questions" });
//    }
// };

export const addQuestions = async (req, res) => {
  try {
    const { testId } = req.params;
    const { file } = req;

    if (!testId || !file) {
      return res.status(400).json({ msg: "Invalid testId or file missing" });
    }

    const test = await Test.findById(testId);
    if (!test) return res.status(404).json({ msg: "Test not found" });

    // Parse Excel
    const workbook = xlsx.read(file.buffer, { type: "buffer" });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const jsonData = xlsx.utils.sheet_to_json(worksheet);

    if (!jsonData.length) {
      return res.status(400).json({ msg: "Excel file is empty" });
    }

    // ✅ Check if headers are correct
    const headers = Object.keys(jsonData[0]);
    if (!headers.includes("questionText") || !headers.includes("answerText")) {
      return res.status(400).json({
        msg: "Excel file headers should be 'questionText' and 'answerText'",
      });
    }

    // Extract and save questions + answers
    const questionDocs = [];
    const answerDocs = [];

    for (const row of jsonData) {
      if (!row.questionText || !row.answerText) continue;

      const qDoc = await Question.create({
        testId,
        questionText: row.questionText,
      });

      const aDoc = await TestAnswer.create({
        testId,
        answerText: row.answerText,
      });

      questionDocs.push(qDoc);
      answerDocs.push(aDoc);
    }

    // Push to test model
    test.questions.push(...questionDocs.map((q) => q._id));
    test.answers.push(...answerDocs.map((a) => a._id));
    await test.save();

    res.status(200).json({
      msg: "Questions and Answers added successfully from Excel",
      questionsAdded: questionDocs.length,
      answersAdded: answerDocs.length,
    });
  } catch (err) {
    console.error("Add questions error:", err);
    res
      .status(500)
      .json({ msg: "Server error while adding questions/answers" });
  }
};


export const removeTest = async (req, res) => {
   try {
      const { testId } = req.params
      if (!testId) return res.status(400).json("Enter testID")
      await Test.findByIdAndDelete(testId)
      return res.status(200).json({ msg: "Test removed" })
   } catch (error) {
      res.status(500).json({ msg: "Error removing test" });
   }
}

// Add more students to a test
export const addStudents = async (req, res) => {
   try {
      const { testId } = req.params;
      let { scholarIds } = req.body;
      if (typeof scholarIds === "string") scholarIds = [scholarIds];
      if (!Array.isArray(scholarIds) || !scholarIds.length)
         return res.status(400).json({ msg: "No student IDs provided" });

      const students = await Student.find({ scholarId: { $in: scholarIds } });
      const test = await Test.findById(testId);
      if (!test) return res.status(404).json({ msg: "Test not found" });

      let added = [];
      for (const st of students) {
         if (!test.students.some(id => id.toString() === st._id.toString())) {
            test.students.push(st._id);
            added.push(st._id);
         }
      }
      await test.save();
      res.status(200).json({ msg: "Students added", added });
   } catch (err) {
      res.status(500).json({ msg: "Error adding students" });
   }
};


// Remove question from a test
export const removeQuestion = async (req, res) => {
   try {
      const { testId, questionId } = req.params;
      const test = await Test.findById(testId)
      if (!test) return res.status(404).json({ msg: "Test not found" });
      test.questions = test.questions.filter(qid => qid.toString() !== questionId);
      await test.save();
      await Question.findByIdAndDelete(questionId);
      res.status(200).json({ msg: "Question removed" });
   } catch (err) {
      res.status(500).json({ msg: "Error removing question" });
   }
};


export const findtestfromId = async (req, res) => {
   try {
      console.log("findtestfromId is called");
    const { testId } = req.params;
    const test = await Test.findById(testId).select("title");
    if (!test) return res.status(404).json({ message: "Test not found" });
    res.json({ title: test.title });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};


