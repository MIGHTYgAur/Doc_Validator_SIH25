import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import DocumentAuthSystemDemo from './components/Demo.jsx'
import UserAuthForm from './components/userReg'
import InstituteRegisterForm from './components/InstituteReg'

function App() {
  return (
    <Router>
        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<DocumentAuthSystemDemo />} />
            <Route path="/login" element={
              <UserAuthForm 
                isLogin={true}
                onToggle={() => console.log('Toggle login/register')}
                onSubmit={(data) => console.log('Form submitted:', data)}
              />
            } />

            <Route path="/institute-register" element={
              <InstituteRegisterForm 
                onSubmit={(data) => console.log('Institute registered:', data)}
              />
            } />
          </Routes>
        </main>
    </Router>
  );
}


export default App;