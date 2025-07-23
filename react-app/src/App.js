import React, { useState, useEffect } from 'react';
import InputMonitor from './components/InputMonitor';
import SearchResults from './components/SearchResults';
import './App.css';

function App() {
  const [currentInputText, setCurrentInputText] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  return (
    <div className="App">
      <div className="app-container">
        <div className="header">
          <h1>🤖 ChatGPT Augmenter React App</h1>
          <p className="subtitle">Monitor your text input and search through documents</p>
        </div>
        
        <InputMonitor 
          currentInputText={currentInputText}
          setCurrentInputText={setCurrentInputText}
          lastUpdated={lastUpdated}
          setLastUpdated={setLastUpdated}
          onSearch={setSearchResults}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
        />
        
        {searchResults && (
          <SearchResults 
            results={searchResults}
            onClose={() => setSearchResults(null)}
          />
        )}
      </div>
    </div>
  );
}

export default App;
