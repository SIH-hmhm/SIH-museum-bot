import express from 'express';
import dotenv from 'dotenv';
import cors from "cors";
import connectToDB from './DB/connectToDB.js';
import botRoute from './routes/botRoute.js';
import userRoutes from './routes/userRoutes.js';


// Configuring the environment variables
dotenv.config();

// Creating an express app
const app = express();

// Middleware to parse the incoming request body into JSON format
app.use(express.json());

// Middleware to enable CORS (Cross-Origin Resource Sharing) basically it allows the server to accept requests from the frontend on a different domain or server
app.use(cors());


// Routes
app.use('/api',botRoute);
app.use('/api/users', userRoutes); 


// Starting the server
app.listen(process.env.PORT,()=>{
    connectToDB();
    console.log(`Server Started at ${process.env.PORT}`);
})
