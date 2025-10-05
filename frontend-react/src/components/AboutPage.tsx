import React from 'react';
import './AboutPage.css';
import exerciseImage from '../assets/exercise.jpg';

const AboutPage: React.FC = () => {
  return (
    <main className="about-us">
      <div className="about-text">
        <h1>About Us</h1>
        <p>
          PosePal aims to bridge the accessibility gap of exercise starting in one simple location: your home. 
          We offer a new way to enhance your workouts at home with webcam tracking video technology and a 
          virtual assistant integrated into our software. With our software, you can create your personally 
          tailored workout routine and get feedback on your progress at no cost. Just set up a device with a 
          camera attachment and start moving!
        </p>
        <p>
          All interactions with the bot are secure and private. We use a model trained with an existing API to 
          provide accurate comparisons and advice on your exercise habits, but no videos taken by the webcam 
          will be shared to the public.
        </p>
      </div>
      <div className="about-image">
        <img src={exerciseImage} alt="Exercise Image" />
      </div>
    </main>
  );
};

export default AboutPage;
