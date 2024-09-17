import './App.css'
import Chatbot from './Components/test'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginForm from './Pages/Login';
import SignupForm from './Pages/SignUp';

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Chatbot />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/signup" element={<SignupForm />} />

      </Routes>
    </Router>
  )
}

export default App
