import React, { useState, useEffect } from 'react';

const StartupProgressBar = () => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Starting up...');

  useEffect(() => {
    const steps = [
      { percent: 20, message: 'Loading configuration...' },
      { percent: 40, message: 'Initializing services...' },
      { percent: 60, message: 'Connecting to database...' },
      { percent: 80, message: 'Starting backend...' },
      { percent: 100, message: 'Startup complete!' },
    ];

    let currentStep = 0;

    const interval = setInterval(() => {
      if (currentStep < steps.length) {
        setProgress(steps[currentStep].percent);
        setStatus(steps[currentStep].message);
        currentStep++;
      } else {
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="startup-progress-container">
      <div className="progress-bar-background">
        <div
          className="progress-bar-fill"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="progress-status">{status}</div>
    </div>
  );
};

export default StartupProgressBar;
