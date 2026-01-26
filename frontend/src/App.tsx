import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ScenarioManager from './components/ScenarioManager';
import CustomerJourneyMap from './components/CustomerJourneyMap';
import KPIAnalytics from './components/KPIAnalytics';
import Settings from './components/Settings';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import NetworkStatus from './components/NetworkStatus';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen flex flex-col bg-white">
          <NetworkStatus />
          <Navigation />
          <main className="flex-1 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/scenarios" element={<ScenarioManager />} />
              <Route path="/journey-map" element={<CustomerJourneyMap />} />
              <Route path="/kpi" element={<KPIAnalytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
