import React, { useState, useEffect } from 'react';
import CameraComponent from './CameraComponent';
import './WorkoutPage.css';

interface WorkoutMetrics {
  reps: number;
  avgScore: number;
  flags: string[];
  durationSec: number;
  timestamp: string;
}

const WorkoutPage: React.FC = () => {
  const [selectedExercise, setSelectedExercise] = useState('squat');
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [repCount, setRepCount] = useState(0);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [workoutMetrics, setWorkoutMetrics] = useState<WorkoutMetrics[]>([]);

  const exercises = [
    { id: 'squat', name: 'Squats', description: 'Lower body strength exercise' },
    { id: 'pushup', name: 'Push-ups', description: 'Upper body strength exercise' },
    { id: 'plank', name: 'Plank', description: 'Core stability exercise' },
    { id: 'lunges', name: 'Lunges', description: 'Lower body balance exercise' }
  ];

  const startWorkoutSession = async () => {
    try {
      const response = await fetch('http://localhost:8000/sessions/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          exercise: selectedExercise,
          user_id: 'user_123' // In a real app, this would come from auth
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setIsSessionActive(true);
        setSessionStartTime(new Date());
        setRepCount(0);
        setWorkoutMetrics([]);
      } else {
        console.error('Failed to start session');
      }
    } catch (error) {
      console.error('Error starting session:', error);
    }
  };

  const stopWorkoutSession = async () => {
    if (!sessionId) return;

    try {
      const now = new Date().toISOString();
      const response = await fetch(`http://localhost:8000/sessions/${sessionId}/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ts: now
        }),
      });

      if (response.ok) {
        setIsSessionActive(false);
        setSessionId(null);
        setSessionStartTime(null);
      } else {
        console.error('Failed to stop session');
      }
    } catch (error) {
      console.error('Error stopping session:', error);
    }
  };

  const sendWorkoutMetrics = async (metrics: WorkoutMetrics) => {
    if (!sessionId) return;

    try {
      const response = await fetch(`http://localhost:8000/sessions/${sessionId}/metrics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metrics),
      });

      if (response.ok) {
        setWorkoutMetrics(prev => [...prev, metrics]);
      } else {
        console.error('Failed to send metrics');
      }
    } catch (error) {
      console.error('Error sending metrics:', error);
    }
  };

  const handleRepCount = (count: number) => {
    setRepCount(count);
    
    if (isSessionActive && sessionStartTime) {
      const duration = Math.floor((Date.now() - sessionStartTime.getTime()) / 1000);
      const metrics: WorkoutMetrics = {
        reps: count,
        avgScore: 0.8, // This would be calculated from pose analysis
        flags: [], // This would be populated based on form analysis
        durationSec: duration,
        timestamp: new Date().toISOString()
      };
      
      sendWorkoutMetrics(metrics);
    }
  };

  const handlePoseDetected = (landmarks: any) => {
    // This is where you would analyze the pose for form feedback
    // For now, we'll just log that pose was detected
    console.log('Pose detected:', landmarks);
  };

  const handleWorkoutStart = () => {
    startWorkoutSession();
  };

  const handleWorkoutStop = () => {
    stopWorkoutSession();
  };

  return (
    <div className="workout-page">
      <div className="workout-header">
        <h1>Camera-Assisted Workout</h1>
        <p>Get real-time feedback on your form and track your progress</p>
      </div>

      <div className="workout-content">
        <div className="exercise-selection">
          <h2>Select Exercise</h2>
          <div className="exercise-grid">
            {exercises.map((exercise) => (
              <div
                key={exercise.id}
                className={`exercise-card ${selectedExercise === exercise.id ? 'selected' : ''}`}
                onClick={() => setSelectedExercise(exercise.id)}
              >
                <h3>{exercise.name}</h3>
                <p>{exercise.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="camera-section">
          <CameraComponent
            onPoseDetected={handlePoseDetected}
            onRepCount={handleRepCount}
            onWorkoutStart={handleWorkoutStart}
            onWorkoutStop={handleWorkoutStop}
            exercise={selectedExercise}
          />
        </div>

        {isSessionActive && (
          <div className="active-session-info">
            <div className="session-info">
              <h3>Active Session</h3>
              <p>Exercise: {exercises.find(e => e.id === selectedExercise)?.name}</p>
              <p>Reps: {repCount}</p>
              <p>Duration: {sessionStartTime ? Math.floor((Date.now() - sessionStartTime.getTime()) / 1000) : 0}s</p>
            </div>
          </div>
        )}

        {workoutMetrics.length > 0 && (
          <div className="workout-history">
            <h3>Workout History</h3>
            <div className="metrics-list">
              {workoutMetrics.map((metric, index) => (
                <div key={index} className="metric-item">
                  <span>Reps: {metric.reps}</span>
                  <span>Score: {metric.avgScore}</span>
                  <span>Duration: {metric.durationSec}s</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkoutPage;
