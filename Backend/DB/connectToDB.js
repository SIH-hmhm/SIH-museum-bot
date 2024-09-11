import mongoose from 'mongoose';

const connectToDB = async () => {
  try {
    // Connect to MongoDB using the MONGO_URI from the .env file
    await mongoose.connect(process.env.MONGO_URI);
    console.log('Connected to MongoDB');
  } catch (error) {
    console.log('Error connecting to MongoDB:', error);
  }
}

export default connectToDB;