import React, { useRef, useEffect, useState } from 'react';
import './CameraComponent.css';

const SERVER_URL = 'http://127.0.0.1:8000';

interface CameraComponentProps {
  onPoseDetected?: (landmarks: any) => void;
  onRepCount?: (count: number) => void;
  onWorkoutStart?: () => void;
  onWorkoutStop?: () => void;
  exercise?: string;
}

const CameraComponent: React.FC<CameraComponentProps> = ({  
  onRepCount, 
  onWorkoutStart,
  onWorkoutStop,
  exercise = 'squat' 
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
      videoRef.current.play();
      setIsWorkoutActive(true);
      
      // Start drawing video to canvas
      drawVideoToCanvas();
      
      // Start rep counting simulation
      startRepCounting();
      
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

  const startRepCounting = () => {
    // Simple demo rep counting - in real implementation this would use pose detection
    const interval = setInterval(() => {
      if (!isWorkoutActive) {
        clearInterval(interval);
        return;
      }
      
      // Simulate rep detection
      if (Math.random() > 0.7) {
        const newCount = repCount + 1;
        setRepCount(newCount);
        setIsDetecting(true);
        
        if (onRepCount) {
          onRepCount(newCount);
        }
        
        // Reset detection state after a short delay
        setTimeout(() => setIsDetecting(false), 1000);
      }
    }, 2000);
  };

  const drawVideoToCanvas = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    
    // Draw a simple overlay to show the component is working
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    ctx.strokeRect(50, 50, canvas.width - 100, canvas.height - 100);
    
    ctx.fillStyle = '#FF0000';
    ctx.font = '20px Arial';
    ctx.fillText('Camera Active - Pose Detection Coming Soon', 50, 50);
    
    // Draw rep count
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 24px Arial';
    ctx.fillText(`Reps: ${repCount}`, 50, canvas.height - 50);
    
    if (isDetecting) {
      ctx.fillStyle = '#00FF00';
      ctx.font = 'bold 20px Arial';
      ctx.fillText('REP DETECTED!', 50, canvas.height - 80);
    }
    return canvas;
  };

  const sendFrameToBackend = (canvas: HTMLCanvasElement | undefined) => {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Get base64 data without the data URL prefix
    const dataURL = canvas.toDataURL('image/jpeg');
    const base64Data = dataURL.split(',')[1]; // Remove "data:image/jpeg;base64," prefix
    
    console.log('Sending frame to backend:', {
      url: `${SERVER_URL}/frames`,
      dataLength: base64Data.length,
      dataPreview: base64Data.substring(0, 50) + '...'
    });
    
    fetch(`${SERVER_URL}/frames`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ frame: base64Data }),
    })
    .then(response => {
      console.log('Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Frame processed successfully:', data);
    })
    .catch(error => {
      console.error('Error sending frame:', error);
    });
  };

  useEffect(() => {
    if (isWorkoutActive && videoRef.current) {
      const interval = setInterval(() => {
        const canvas = drawVideoToCanvas();
        sendFrameToBackend(canvas);
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isWorkoutActive, repCount, isDetecting]);

  return (
    <div className="camera-container">
      <div className="camera-wrapper">
        <video
          ref={videoRef}
          className="camera-video"
          style={{ display: 'none' }}
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

      <div className="workout-stats">
        <div className="stat-item">
          <span className="stat-label">Reps:</span>
          <span className="stat-value">{repCount}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Exercise:</span>
          <span className="stat-value">{exercise}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Status:</span>
          <span className="stat-value">{isDetecting ? 'Rep Detected!' : 'Ready'}</span>
        </div>
      </div>
      
      <div className="demo-notice">
        <p><strong>Demo Mode:</strong> This is a simplified version. Full pose detection with MediaPipe will be added in the next update.</p>
      </div>
    </div>
  );
};

export default CameraComponent;
