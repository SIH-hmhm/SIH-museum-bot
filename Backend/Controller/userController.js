import User from "../Models/userModel.js"
import generateToken from "../utils/generateToken.js";
import bcrypt from "bcryptjs";


//This function is used to sign up a new user

export const signUp = async (req, res) => {

    // Destructuring the name, email, password and confirmPassword from the request body request body means the data coming from the frontend form

    const { name, email, password, confirmPassword } = req.body;

    //try and catch block is used to handle the errors that may occur during the execution of the code try will contain the code that may throw an error and catch will handle the error

    try {

        //Checking if the password and confirmPassword are same or not if not then it will return an error
        if (password !== confirmPassword) {
            return res.status(400).json({ error: "Passwords do not match" });
        }
        //Checking if the user already exists or not if exists then it will return an error
        const existingUser = await User.findOne({ email });
        //If the user already exists then it will return an error
        if (existingUser) {
            return res.status(400).json({ error: "User already exists" });
        }
        //Hashing the password using bcrypt library to store the password in the database
        const hashedPassword = await bcrypt.hash(password, 12);

        //Creating a new user in the database
        const newUser = await User.create({ name, email, password : hashedPassword });
        //If the user is created then it will return the user and the token
        if (newUser) {
            const token = generateToken(newUser._id, res);
            newUser.password = undefined;
            res.status(201).json({ newUser, token });
        }

    } 
    //If any error occurs then it will return the error
    catch (error) {
        res.status(500).json({ error: error.message });
    }
}

export const login = async (req, res) => {
    // Destructuring the email and password from the request body request body means the data coming from the frontend form
    const { email, password } = req.body;
    //try and catch block is used to handle the errors that may occur during the execution of the code try will contain the code that may throw an error and catch will handle the error    
    try {
        //Checking if the user already exists or not if not then it will return an error
        const existingUser = await User.findOne({ email });

        if (!existingUser) {
            return res.status(404).json({ error: "User does not exist" });
        }
        //Checking if the password is correct or not if not then it will return an error
        const isPasswordCorrect = await bcrypt.compare(password, existingUser.password);
        //If the password is not correct then it will return an error
        if(!isPasswordCorrect){
            return res.status(400).json({ error: "Invalid credentials" });
        }
        //If the user exists and the password is correct then it will return the user and the token
        if (existingUser && isPasswordCorrect) {
            const token = generateToken(existingUser._id, res);
            existingUser.password = undefined;
            res.status(200).json({ existingUser, token });
        }
        //If any error occurs then it will return the error
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
}
//This function is used to logout the user
export const logout = (req, res) => {
    //Clearing the token from the cookie
    res.clearCookie("token");
    res.status(200).json({ message: "Logged out successfully" });
}