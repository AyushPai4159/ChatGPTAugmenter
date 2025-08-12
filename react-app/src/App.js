import React, { useState, useEffect } from 'react';
import InputMonitor from './components/InputMonitor';
import SearchResults from './components/SearchResults';
import FileUpload from './components/FileUpload';
import './App.css';

// Simple UUID v4 generator
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

function App() {
  const [currentInputText, setCurrentInputText] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [userUUID, setUserUUID] = useState(null);

  // Generate UUID when app starts
  useEffect(() => {
    const uuid = generateUUID();
    setUserUUID(uuid);
    
    // Console log that we're sending to backend (simulated)
    console.log('Sending UUID to backend:', uuid);
    
    // Console log the UUID after finishing
    console.log('Generated User UUID:', uuid);
  }, []);

  return (
    <div className="App">
      <div className="app-container">
        <div className="header">
          <h1>🤖 ChatGPT Augmenter React App</h1>
          <p className="subtitle">Monitor your text input and search through documents</p>
        </div>
        
        <FileUpload userUUID={userUUID} />
        
        <InputMonitor 
          currentInputText={currentInputText}
          setCurrentInputText={setCurrentInputText}
          lastUpdated={lastUpdated}
          setLastUpdated={setLastUpdated}
          onSearch={setSearchResults}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
          userUUID={userUUID}
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
