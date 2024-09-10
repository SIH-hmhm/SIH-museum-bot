const express = require('express');
require('dotenv').config();
const mongoose = require('mongoose');
const bodyparser = require('body-parser');
const cors = require("cors");
const route = require('./routes/route');

const app = express();
app.use(bodyparser.json());
app.use(cors());

mongoose.connect("mongodb://localhost:27017/SIH-museum-bot")
.then(() => {
    console.log("Connected!")
})
.catch(() =>{
    console.log("Error!")
})

app.use('/api',route)


app.listen(process.env.PORT,()=>{
    console.log(`Server Started at ${process.env.PORT}`);
})
