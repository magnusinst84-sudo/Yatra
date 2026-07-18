import React, { useState } from 'react';
import Navbar from './components/Navbar.jsx';
import Home from './pages/Home.jsx';
import History from './pages/History.jsx';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');

  return (
    <div className="min-h-screen bg-darkBg text-white relative flex flex-col">
      {/* Premium Navbar */}
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />

      {/* Main Pages with Fade In / Slide Up page transitions */}
      <main className="flex-grow flex flex-col">
        {currentPage === 'home' ? (
          <div key="home" className="animate-fade-in flex-grow flex flex-col">
            <Home />
          </div>
        ) : (
          <div key="history" className="animate-fade-in flex-grow flex flex-col">
            <History />
          </div>
        )}
      </main>
    </div>
  );
}
