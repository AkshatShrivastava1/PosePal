# PosePal - Camera-Assisted Workout App

A React-based fitness application that uses computer vision to provide real-time feedback on exercise form and track workout progress.

## Features

- 🎥 **Real-time Camera Integration**: Uses MediaPipe for pose detection
- 🏃‍♂️ **Exercise Tracking**: Automatic rep counting for various exercises
- 📊 **Workout Analytics**: Track progress and form feedback
- 🎨 **Modern UI**: Responsive design with smooth animations
- 🔗 **Backend Integration**: Connects to FastAPI backend for session management

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Computer Vision**: MediaPipe Pose Detection
- **Styling**: CSS3 with modern gradients and animations
- **Backend**: FastAPI (Python)
- **Routing**: React Router

## Setup Instructions

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Python 3.8+ (for backend)
- Webcam access

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend-react
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Usage

1. **Start the Application**: Open both frontend and backend servers
2. **Select Exercise**: Choose from Squats, Push-ups, Plank, or Lunges
3. **Enable Camera**: Click "Start Camera" to begin pose detection
4. **Start Workout**: Click "Start Workout Session" to begin tracking
5. **Exercise**: Perform the selected exercise while the app tracks your form
6. **View Progress**: Monitor rep count and form feedback in real-time
7. **End Session**: Click "End Session" to save your workout data

## Exercise Detection

The app currently supports:

- **Squats**: Detects hip and knee position for rep counting
- **Push-ups**: Upper body pose analysis (coming soon)
- **Plank**: Core stability tracking (coming soon)
- **Lunges**: Balance and form analysis (coming soon)

## API Endpoints

- `POST /sessions/start` - Start a new workout session
- `POST /sessions/{id}/metrics` - Send workout metrics
- `POST /sessions/{id}/stop` - End workout session
- `GET /sessions/{id}/summary` - Get session summary

## Development

### Project Structure

```
frontend-react/
├── src/
│   ├── components/
│   │   ├── CameraComponent.tsx    # MediaPipe integration
│   │   ├── WorkoutPage.tsx       # Main workout interface
│   │   ├── LandingPage.tsx       # Home page
│   │   ├── AboutPage.tsx         # About page
│   │   └── Header.tsx            # Navigation
│   ├── App.tsx                   # Main app component
│   └── main.tsx                  # Entry point
├── public/
│   └── assets/                   # Static assets
└── package.json
```

### Key Components

- **CameraComponent**: Handles MediaPipe pose detection and rep counting
- **WorkoutPage**: Main workout interface with exercise selection
- **WorkoutSession**: Manages session state and API communication

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Security & Privacy

- All camera data is processed locally
- No video recordings are stored or transmitted
- Only pose landmark coordinates are used for analysis
- Session data is stored locally in the backend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details