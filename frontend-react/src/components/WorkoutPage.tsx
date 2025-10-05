import React, { useState } from 'react';
import CameraComponent from './CameraComponent';
import PostureAnalysisCard from './PostureAnalysisCard';
import { API_URLS } from '../constants/serverConfig';
import './WorkoutPage.css';

interface WorkoutMetrics {
  reps: number;
  durationSec: number;
  timestamp: string;
}

interface MetricsIngest {
  reps: number;
  avg_score: number;
  duration_sec: number;
  ts: string; // ISO string format
}

interface PostureSuggestion {
  category: string;
  issue: string;
  suggestion: string;
  priority: 'High' | 'Medium' | 'Low';
}

interface PostureAnalysis {
  overall_assessment: string;
  strengths: string[];
  areas_for_improvement: string[];
  specific_suggestions: PostureSuggestion[];
  exercise_specific_tips: string[];
  next_session_focus: string;
}

const WorkoutPage: React.FC = () => {
  const [selectedExercise, setSelectedExercise] = useState('squat');
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [repCount, setRepCount] = useState(0);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [workoutMetrics, setWorkoutMetrics] = useState<WorkoutMetrics[]>([]);
  
  // Posture analysis state
  const [postureAnalysis, setPostureAnalysis] = useState<PostureAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [completedSessionId, setCompletedSessionId] = useState<number | null>(null);

  const exercises = [
    { id: 'squat', name: 'Squats', description: 'Lower body strength exercise' },
    { id: 'pushup', name: 'Push-ups', description: 'Upper body strength exercise' },
    { id: 'plank', name: 'Plank', description: 'Core stability exercise' },
    { id: 'lunges', name: 'Lunges', description: 'Lower body balance exercise' }
  ];

  const startWorkoutSession = async () => {
    try {
      const response = await fetch(API_URLS.SESSIONS + '/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          exercise: selectedExercise
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setIsSessionActive(true);
        setSessionStartTime(new Date());
        setRepCount(0);
        setWorkoutMetrics([]);
        console.log(`Session started with id: ${data.session_id}`);
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
      const response = await fetch(API_URLS.SESSIONS + `/${sessionId}/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ts: now
        }),
      });

      if (response.ok) {
        console.log(`Session stopped with id: ${sessionId}`);
        setIsSessionActive(false);
        setCompletedSessionId(sessionId);
        setSessionId(null);
        setSessionStartTime(null);
        
        // Automatically trigger posture analysis
        await analyzeSessionPosture(sessionId);
      } else {
        console.error('Failed to stop session');
      }
    } catch (error) {
      console.error('Error stopping session:', error);
    }
  };

  const analyzeSessionPosture = async (sessionIdToAnalyze: number) => {
    setIsAnalyzing(true);
    setAnalysisError(null);
    setPostureAnalysis(null);

    try {
      const response = await fetch(`${API_URLS.ANALYSIS}/analyze-and-cleanup/${sessionIdToAnalyze}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.analysis && data.analysis.suggestions) {
          setPostureAnalysis(data.analysis.suggestions);
        } else {
          setAnalysisError('Analysis completed but no suggestions were generated');
        }
      } else {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        setAnalysisError(errorData.message || 'Failed to analyze session');
      }
    } catch (error) {
      setAnalysisError('Network error during analysis');
      console.error('Error analyzing session:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const sendWorkoutMetrics = async (metrics: WorkoutMetrics) => {
    if (!sessionId) return;

    // Convert WorkoutMetrics to MetricsIngest format
    const metricsIngest: MetricsIngest = {
      reps: metrics.reps,
      avg_score: 0.0, // Default score since we don't have form scoring yet
      duration_sec: metrics.durationSec,
      ts: metrics.timestamp
    };

    try {
      const response = await fetch(API_URLS.SESSIONS + `/${sessionId}/metrics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metricsIngest),
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
          {isSessionActive && (
            <div className="session-active-notice">
              <p><strong>Session Active:</strong> Exercise selection is locked. Stop the current session to change exercises.</p>
            </div>
          )}
          <div className={`exercise-grid ${isSessionActive ? 'disabled' : ''}`}>
            {exercises.map((exercise) => (
              <div
                key={exercise.id}
                className={`exercise-card ${selectedExercise === exercise.id ? 'selected' : ''} ${isSessionActive ? 'disabled' : ''}`}
                onClick={() => !isSessionActive && setSelectedExercise(exercise.id)}
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
            sessionId={sessionId || undefined}
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

      </div>

      {/* Posture Analysis Card - Full Width */}
      <PostureAnalysisCard
        analysis={postureAnalysis}
        isLoading={isAnalyzing}
        error={analysisError}
        sessionId={completedSessionId}
      />
    </div>
  );
};

export default WorkoutPage;
