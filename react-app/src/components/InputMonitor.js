import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './InputMonitor.css';

const InputMonitor = ({ 
  currentInputText, 
  setCurrentInputText, 
  lastUpdated, 
  setLastUpdated,
  onSearch,
  isLoading,
  setIsLoading,
  userUUID
}) => {
  const textareaRef = useRef(null);
  const [characterCount, setCharacterCount] = useState(0);

  useEffect(() => {
    setCharacterCount(currentInputText.length);
  }, [currentInputText]);

  const handleTextChange = (e) => {
    const newText = e.target.value;
    setCurrentInputText(newText);
    setLastUpdated(new Date().toISOString());
  };

  const handleClearText = () => {
    setCurrentInputText('');
    setLastUpdated(new Date().toISOString());
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };



  const integrateBackend = async () => {
    try {
      const response = await axios.post('/search', {
        query: currentInputText.trim(),
        top_k: 6
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      onSearch(response.data);
    } catch (error) {
      console.error('Search error:', error);
      let errorMessage = 'Search failed. ';
      
      if (error.message.includes('Network Error') || error.code === 'ERR_NETWORK') {
        errorMessage += 'Make sure your Flask server is running on localhost:5000';
      } else {
        errorMessage += error.message;
      }
      
      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }

  const handleSearch = async () => {
    if (!currentInputText.trim()) {
      alert('Please enter some text to search');
      return;
    }

    setIsLoading(true);
    await integrateBackend();
  };

  const formatLastUpdated = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return `Last updated: ${date.toLocaleTimeString()}`;
  };


  
//-----------------------------------------------------------------------------------------------------------------------------------------
  // HTML for component w/ dynamically rendered TypeScript-HTML


  return (
    <div className="input-monitor">
      <div className="input-container">
        <div className="input-header">
          <label className="input-label">
            Enter your text to monitor and search:
          </label>
          <div className="char-count">
            {characterCount} characters
          </div>
        </div>
        
        <textarea
          ref={textareaRef}
          value={currentInputText}
          onChange={handleTextChange}
          placeholder="Type your message here... This simulates the ChatGPT input field"
          className="input-textarea"
          rows={6}
        />
        
        <div className="button-container">
          <button
            onClick={handleClearText}
            className="clear-btn"
            disabled={!currentInputText}
          >
            🗑️ Clear Text
          </button>
          
          <button
            onClick={handleSearch}
            className="search-btn"
            disabled={!currentInputText.trim() || isLoading}
          >
            {isLoading ? '🔄 Searching...' : '🔍 Search Documents'}
          </button>
        </div>
        
        {lastUpdated && (
          <div className="last-updated">
            {formatLastUpdated(lastUpdated)}
          </div>
        )}
        
        {!currentInputText && (
          <div className="no-input">
            No input detected. Start typing to see the text here.
          </div>
        )}
      </div>
    </div>
  );
};

export default InputMonitor;
