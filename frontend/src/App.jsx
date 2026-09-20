import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing.jsx'
import Console from './pages/Console.jsx'
import Auth from './pages/Auth.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/console" element={<Console />} />
        <Route path="/login" element={<Auth initialMode="login" />} />
        <Route path="/signup" element={<Auth initialMode="signup" />} />
      </Routes>
    </BrowserRouter>
  )
}
