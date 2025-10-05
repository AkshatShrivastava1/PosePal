import React, { useRef, useEffect, useState } from 'react';
import './CameraComponent.css';
import { API_URLS } from '../constants/serverConfig';

interface CameraComponentProps {
  onPoseDetected?: (landmarks: any) => void;
  onRepCount?: (count: number) => void;
  onWorkoutStart?: () => void;
  onWorkoutStop?: () => void;
  exercise?: string;
  sessionId?: number;
}

const CameraComponent: React.FC<CameraComponentProps> = ({  
  onRepCount, 
  onWorkoutStart,
  onWorkoutStop,
  exercise = 'squat',
  sessionId
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isWorkoutActive, setIsWorkoutActive] = useState(false);
  const [repCount, setRepCount] = useState(0);
  const [isDetecting, setIsDetecting] = useState(false);

  const startWorkout = async () => {
    if (!videoRef.current) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      videoRef.current.srcObject = stream;
      
      // Wait for video to be ready before starting
      videoRef.current.onloadedmetadata = () => {
        videoRef.current?.play();
        setIsWorkoutActive(true);
        console.log('Video loaded and playing');
      };
      
      // Rep counting is now handled by backend pose analysis
      
      // Notify parent component
      if (onWorkoutStart) {
        onWorkoutStart();
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Could not access camera. Please ensure camera permissions are granted.');
    }
  };

  const stopWorkout = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsWorkoutActive(false);
    setIsDetecting(false);
    
    // Notify parent component
    if (onWorkoutStop) {
      onWorkoutStop();
    }
  };


  const drawVideoToCanvas = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Ensure video is ready and has dimensions
    if (videoRef.current.videoWidth === 0 || videoRef.current.videoHeight === 0) {
      return;
    }
    
    // Clear canvas first
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw video frame
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    
    if (isDetecting) {
      ctx.fillStyle = '#00FF00';
      ctx.font = 'bold 20px Arial';
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.strokeText('REP DETECTED!', 50, canvas.height - 80);
      ctx.fillText('REP DETECTED!', 50, canvas.height - 80);
    }
    
    return canvas;
  };

  const sendFrameToBackend = (canvas: HTMLCanvasElement | undefined) => {
    if (!canvas || !sessionId) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Get base64 data without the data URL prefix
    const dataURL = canvas.toDataURL('image/jpeg');
    const base64Data = dataURL.split(',')[1]; // Remove "data:image/jpeg;base64," prefix
    
    fetch(API_URLS.FRAMES + `/${sessionId}`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ frame: base64Data }),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Handle rep counting from backend
      if (data.result && data.result.current_rep_count !== undefined) {
        const newCount = data.result.current_rep_count;
        setRepCount(newCount);
        
        if (onRepCount) {
          onRepCount(newCount);
        }
      }
      
      // Handle rep completion detection
      if (data.result && data.result.rep_completed) {
        // Show rep detected indicator
        setIsDetecting(true);
        setTimeout(() => setIsDetecting(false), 2000);
      }
    })
    .catch(error => {
      console.error('Error sending frame:', error);
    });
  };

  // Continuous canvas drawing when workout is active
  useEffect(() => {
    if (isWorkoutActive && videoRef.current) {
      const drawFrame = () => {
        drawVideoToCanvas();
        requestAnimationFrame(drawFrame);
      };
      drawFrame();
    }
  }, [isWorkoutActive, repCount, isDetecting]);

  // Send frames to backend
  useEffect(() => {
    if (isWorkoutActive && sessionId) {
      const interval = setInterval(() => {
        const canvas = canvasRef.current;
        if (canvas) {
          sendFrameToBackend(canvas);
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isWorkoutActive, sessionId]);

  return (
    <div className="camera-container">
      <div className="camera-wrapper">
        <video
          ref={videoRef}
          className="camera-video"
          style={{ display: 'none' }}
          autoPlay
          muted
          playsInline
        />
        <canvas
          ref={canvasRef}
          className="camera-canvas"
          width={640}
          height={480}
        />
      </div>
      
      <div className="camera-controls">
        <button 
          onClick={isWorkoutActive ? stopWorkout : startWorkout}
          className={`workout-btn ${isWorkoutActive ? 'stop' : 'start'}`}
        >
          {isWorkoutActive ? 'Stop Workout' : 'Start Workout'}
        </button>
      </div>
      
      <div className="demo-notice">
        <p><strong>Demo Mode:</strong> This is a simplified version. Full pose detection with MediaPipe will be added in the next update.</p>
      </div>
    </div>
  );
};

export default CameraComponent;
