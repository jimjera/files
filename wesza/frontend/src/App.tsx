import { useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import CreateAppPage from './pages/CreateAppPage';
import AppsListPage from './pages/AppsListPage';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/create-app" element={<CreateAppPage />} />
        <Route path="/my-apps" element={<AppsListPage />} />
      </Routes>
    </div>
  );
}

export default App;
