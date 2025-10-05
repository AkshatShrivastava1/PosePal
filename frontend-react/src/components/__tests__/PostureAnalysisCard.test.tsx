import React from 'react';
import { render, screen } from '@testing-library/react';
import PostureAnalysisCard from './PostureAnalysisCard';

// Mock data for testing
const mockAnalysis = {
  overall_assessment: "Great form overall with room for improvement",
  strengths: ["Consistent depth", "Good alignment"],
  areas_for_improvement: ["Knee tracking", "Core engagement"],
  specific_suggestions: [
    {
      category: "Posture",
      issue: "Knees caving inward",
      suggestion: "Focus on pushing knees out during descent",
      priority: "High" as const
    }
  ],
  exercise_specific_tips: ["Keep chest up throughout movement"],
  next_session_focus: "Work on knee alignment and core stability"
};

describe('PostureAnalysisCard', () => {
  it('renders loading state correctly', () => {
    render(
      <PostureAnalysisCard
        analysis={null}
        isLoading={true}
        error={null}
        sessionId={123}
      />
    );
    
    expect(screen.getByText('🤖 AI Posture Analysis')).toBeInTheDocument();
    expect(screen.getByText('Analyzing your workout...')).toBeInTheDocument();
  });

  it('renders error state correctly', () => {
    render(
      <PostureAnalysisCard
        analysis={null}
        isLoading={false}
        error="Analysis failed"
        sessionId={123}
      />
    );
    
    expect(screen.getByText('🤖 AI Posture Analysis')).toBeInTheDocument();
    expect(screen.getByText('Analysis failed')).toBeInTheDocument();
  });

  it('renders analysis results correctly', () => {
    render(
      <PostureAnalysisCard
        analysis={mockAnalysis}
        isLoading={false}
        error={null}
        sessionId={123}
      />
    );
    
    expect(screen.getByText('🤖 AI Posture Analysis')).toBeInTheDocument();
    expect(screen.getByText('Session #123')).toBeInTheDocument();
    expect(screen.getByText('📊 Overall Assessment')).toBeInTheDocument();
    expect(screen.getByText(mockAnalysis.overall_assessment)).toBeInTheDocument();
    expect(screen.getByText('✅ Strengths')).toBeInTheDocument();
    expect(screen.getByText('🎯 Areas for Improvement')).toBeInTheDocument();
    expect(screen.getByText('💡 Specific Suggestions')).toBeInTheDocument();
    expect(screen.getByText('🏋️ Exercise-Specific Tips')).toBeInTheDocument();
    expect(screen.getByText('🎯 Next Session Focus')).toBeInTheDocument();
  });

  it('does not render when sessionId is null', () => {
    const { container } = render(
      <PostureAnalysisCard
        analysis={mockAnalysis}
        isLoading={false}
        error={null}
        sessionId={null}
      />
    );
    
    expect(container.firstChild).toBeNull();
  });
});
