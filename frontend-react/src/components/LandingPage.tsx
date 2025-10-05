import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage: React.FC = () => {
  return (
    <main className="landing">
      <div className="landing-content">
        <h1>Your Digital Personal Fitness Assistant</h1>
        <p>Correct your form, count your reps, and improve safely at home.</p>
        <Link to="/workout" className="get-moving-btn">Get Started</Link>
      </div>
      <div className="landing-image">
        <img src="/assets/landing.jpg" alt="Exercise Image" />
      </div>
    </main>
  );
};

export default LandingPage;
