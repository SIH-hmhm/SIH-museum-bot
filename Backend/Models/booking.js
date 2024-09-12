import mongoose from "mongoose";

const bookingSchema = new mongoose.Schema({
    bookingDate: {
        type: Date,
        required: true,
    },
    bookingTime: {
        type: String,
        required: true,
    },
    bookingStatus: {
        type: String,
        required: true,
    },
    bookingId: {
        type: String,
        required: true,
    },
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "User",
        required: true,
    },
    createdAt: {
        type: Date,
        default: Date.now,
    }
});

const Booking = mongoose.model("Booking", bookingSchema);
export default Booking;