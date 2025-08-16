import mongoose from 'mongoose';
import dotenv from "dotenv";

dotenv.config();  

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('MongoDB connected');
  } catch (err) {
    console.error('MongoDB connection error:', err);
    process.exit(1);
  }
};

export default connectDB;



// import mongoose from "mongoose";
// import dotenv from "dotenv";

// dotenv.config();  // ✅ Load .env file

// const connectDB = async () => {
//   try {
//     const conn = await mongoose.connect(process.env.MONGO_URI);
//     console.log(`✅ MongoDB connected: ${conn.connection.host}`);
//   } catch (err) {
//     console.error("❌ MongoDB connection error:", err);
//   }
// };

// export default connectDB;
