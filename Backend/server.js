import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import passport from 'passport';
import session from 'express-session'; // Required for Passport sessions
import connectToDB from './DB/connectToDB.js';
import botRoute from './routes/botRoute.js';
import userRoutes from './routes/userRoutes.js';
import { googleStrategy } from './Controller/userController.js';

// Configuring the environment variables
dotenv.config();

// Creating an express app
const app = express();

// Middleware to parse the incoming request body into JSON format
app.use(express.json());

// Middleware to enable CORS (Cross-Origin Resource Sharing)
app.use(cors());

// Initialize Passport and configure session
app.use(session({
  secret: process.env.JWT_SECRET,  // Replace with a secure key
  resave: false,
  saveUninitialized: false
}));
app.use(passport.initialize());
app.use(passport.session());

// Initialize Google Strategy
googleStrategy();

// Routes
app.use('/api', botRoute);
app.use('/api/users', userRoutes);

// Starting the server
app.listen(process.env.PORT, () => {
  connectToDB();
  console.log(`Server Started at ${process.env.PORT}`);
});
