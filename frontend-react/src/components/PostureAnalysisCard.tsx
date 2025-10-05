import React from 'react';
import './PostureAnalysisCard.css';

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

interface PostureAnalysisCardProps {
  analysis: PostureAnalysis | null;
  isLoading: boolean;
  error: string | null;
  sessionId: number | null;
}

const PostureAnalysisCard: React.FC<PostureAnalysisCardProps> = ({
  analysis,
  isLoading,
  error,
  sessionId
}) => {
  if (!sessionId) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="posture-analysis-card loading">
        <div className="analysis-header">
          <h2>🤖 AI Posture Analysis</h2>
          <div className="loading-spinner">
            <div className="spinner"></div>
            <span>Analyzing your workout...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="posture-analysis-card error">
        <div className="analysis-header">
          <h2>🤖 AI Posture Analysis</h2>
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return null;
  }

  return (
    <div className="posture-analysis-card">
      <div className="analysis-header">
        <h2>🤖 AI Posture Analysis</h2>
      </div>

      <div className="analysis-content">
        {/* Overall Assessment */}
        <div className="analysis-section">
          <h3>📊 Overall Assessment</h3>
          <p className="assessment-text">{analysis.overall_assessment}</p>
        </div>

        {/* Strengths and Areas for Improvement */}
        <div className="analysis-grid">
          <div className="analysis-column">
            <h3>✅ Strengths</h3>
            <ul className="strengths-list">
              {analysis.strengths.map((strength, index) => (
                <li key={index} className="strength-item">
                  <span className="strength-icon">💪</span>
                  {strength}
                </li>
              ))}
            </ul>
          </div>

          <div className="analysis-column">
            <h3>🎯 Areas for Improvement</h3>
            <ul className="improvement-list">
              {analysis.areas_for_improvement.map((area, index) => (
                <li key={index} className="improvement-item">
                  <span className="improvement-icon">🔧</span>
                  {area}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Specific Suggestions */}
        {analysis.specific_suggestions.length > 0 && (
          <div className="analysis-section">
            <h3>💡 Specific Suggestions</h3>
            <div className="suggestions-grid">
              {analysis.specific_suggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-card">
                  <div className="suggestion-header">
                    <span className="suggestion-category">{suggestion.category}</span>
                  </div>
                  <div className="suggestion-content">
                    <h4 className="suggestion-issue">{suggestion.issue}</h4>
                    <p className="suggestion-text">{suggestion.suggestion}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Exercise-Specific Tips */}
        {analysis.exercise_specific_tips.length > 0 && (
          <div className="analysis-section">
            <h3>🏋️ Exercise-Specific Tips</h3>
            <div className="tips-list">
              {analysis.exercise_specific_tips.map((tip, index) => (
                <div key={index} className="tip-item">
                  <span className="tip-icon">💡</span>
                  <span className="tip-text">{tip}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Session Focus */}
        <div className="analysis-section next-session">
          <h3>🎯 Next Session Focus</h3>
          <div className="next-session-content">
            <span className="next-session-icon">🚀</span>
            <span className="next-session-text">{analysis.next_session_focus}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostureAnalysisCard;
