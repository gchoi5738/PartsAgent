import React from 'react';
import Chat from './components/Chat';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ProductDetail, InstallationGuide } from './pages';
import FAQ from './pages/FAQ';



const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Chat />} />
        <Route path="/products/:part_number" element={<ProductDetail />} />
        <Route path="/products/:part_number/installation-guide" element={<InstallationGuide />} />
        <Route path="/faq" element={<FAQ />} />
      </Routes>
    </Router>
  );
};

export default App;