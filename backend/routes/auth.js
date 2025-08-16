// routes/auth.js
import express from "express";
import upload from "../middlewares/multerMiddleware.js";

import {
   registerUser,
   loginUser,
   logoutUser,
   refreshAccessToken,
   sendOtp,
   updateUser
} from "../controllers/userController.js";

import { verifyToken, authorizeRoles } from "../middlewares/authMiddleware.js"

const router = express.Router();

router.post("/register", upload.single("image"), registerUser);
router.post("/login", loginUser);
router.post("/logout", verifyToken, logoutUser);
router.get("/refresh", refreshAccessToken);
router.post("/send-otp", sendOtp);
router.put("/update", verifyToken, updateUser)

export default router;
