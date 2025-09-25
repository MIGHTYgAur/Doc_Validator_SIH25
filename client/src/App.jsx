import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DocumentAuthSystem from './components/DocAuth.jsx'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/*" element={<DocumentAuthSystem />} />
      </Routes>
    </Router>
  );
}

export default App;
