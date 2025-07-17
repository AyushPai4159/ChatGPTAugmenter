import React, { useState } from 'react';
import './SearchResults.css';

const SearchResults = ({ results, onClose }) => {
  const [expandedCard, setExpandedCard] = useState(null);

  if (!results) return null;

  const parseMarkdown = (text) => {
    return text
      // Headers
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.*?)__/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/_(.*?)_/g, '<em>$1</em>')
      // Code blocks
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      // Inline code
      .replace(/`(.*?)`/g, '<code>$1</code>')
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
      // Line breaks
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>')
      // Lists
      .replace(/^\* (.*$)/gim, '<li>$1</li>')
      .replace(/^- (.*$)/gim, '<li>$1</li>')
      // Wrap in paragraph tags
      .replace(/^(?!<[h|l|p|d])(.+)$/gim, '<p>$1</p>')
      // Fix list wrapping
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  };

  const toggleExpanded = (index) => {
    setExpandedCard(expandedCard === index ? null : index);
  };

  if (!results.results || results.results.length === 0) {
    return (
      <div className="search-results-overlay">
        <div className="search-results-container">
          <div className="search-results-header">
            <h2>🔍 Search Results</h2>
            <button onClick={onClose} className="close-btn">✕</button>
          </div>
          <div className="no-results">
            🤷‍♂️ No results found for "{results.query}"
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="search-results-overlay">
      <div className="search-results-container">
        <div className="search-results-header">
          <div>
            <h2>🔍 Search Results</h2>
            <p className="query-info">
              Query: "<strong>{results.query}</strong>" | Found {results.results.length} results
            </p>
          </div>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>
        
        <div className="results-list">
          {results.results.map((result, index) => {
            const similarity = Math.round(result.similarity * 100);
            const isExpanded = expandedCard === index;
            
            return (
              <div key={index} className={`result-card ${isExpanded ? 'expanded' : ''}`}>
                <div className="result-header" onClick={() => toggleExpanded(index)}>
                  <div className="result-title">
                    #{index + 1} {result.key}
                  </div>
                  <div className="result-controls">
                    <div className="similarity-badge">{similarity}% match</div>
                    <div className="expand-btn">
                      {isExpanded ? '📖 Collapse' : '📄 Expand'}
                    </div>
                  </div>
                </div>
                
                <div className={`result-content ${isExpanded ? 'expanded' : ''}`}>
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: parseMarkdown(result.content) 
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
        
        <div className="search-footer">
          <button onClick={onClose} className="close-footer-btn">
            Close Results
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchResults;
