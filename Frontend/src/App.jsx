import './App.css'
import Chatbot from './Components/test'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './Pages/Login';
import SignUp from './Pages/SignUp';

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Chatbot />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />

      </Routes>
    </Router>
  )
}

export default App
