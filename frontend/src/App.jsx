import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, MessageSquare } from 'lucide-react';
import Dashboard from './Dashboard';
import Chat from './Chat';
import './index.css';

function Sidebar() {
  const location = useLocation();
  return (
    <div className="sidebar">
      <div className="logo">🌱 <span>AgriChat</span></div>
      <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
        <LayoutDashboard size={20} /> Dashboard
      </Link>
      <Link to="/chat" className={`nav-link ${location.pathname === '/chat' ? 'active' : ''}`}>
        <MessageSquare size={20} /> Chat Simulator
      </Link>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
