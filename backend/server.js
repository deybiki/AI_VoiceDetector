import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import cookieParser from "cookie-parser";

import connectDB from './config/mongo.js';

import authRoutes from './routes/auth.js';
import studentRoutes from './routes/student.js';
import examinerRoutes from './routes/examiner.js';
import testRoutes from './routes/test.js';
import evaluatorRoutes from './routes/evaluator.js';
import detailsRoutes from './routes/details.js';
import testResultRoutes from './routes/testResults.js';
import testAttempt from './routes/testAttempt.js';

import platformFeedbackRouter from "./platformFeedback.js";
// import violationRoutes from "./routes/violation.js";


dotenv.config();
connectDB();

const app = express();

// app.use(cors({
//    origin: "http://localhost:3000",
//    credentials: true
// }));


app.use(cors({
   origin: ["http://localhost:3000", "http://localhost:8501"],
   credentials: true
}));



app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

app.get('/', (req, res) => {
   res.status(200).send('🚀 Server is running!');
});

// Attach all routes here
app.use('/api/auth', authRoutes);
app.use('/api/student', studentRoutes);
app.use('/api/examiner', examinerRoutes);
app.use('/api/test', testRoutes);
app.use('/api/evaluator', evaluatorRoutes);
app.use('/api/details', detailsRoutes);
app.use('/api/testAttempt', testAttempt);
app.use("/api", testResultRoutes);

// app.use("/api", platformFeedbackRouter);
app.use("/api/feedback", platformFeedbackRouter);
// app.use("/api", violationRoutes);


app.listen(5000, () => console.log('Server running on port 5000'));