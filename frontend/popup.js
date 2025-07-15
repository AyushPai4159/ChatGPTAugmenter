// Popup script for ChatGPT Input Monitor
document.addEventListener('DOMContentLoaded', function() {
  const inputTextElement = document.getElementById('inputText');
  const charCountElement = document.getElementById('charCount');
  const statusElement = document.getElementById('status');
  const refreshBtn = document.getElementById('refreshBtn');
  const searchBtn = document.getElementById('searchBtn');
  const searchResults = document.getElementById('searchResults');
  const lastUpdatedElement = document.getElementById('lastUpdated');
  
  let isConnected = false;
  
  // Function to update the display
  function updateDisplay(data) {
    const { currentInputText = '', isConnected: connected = false, lastUpdated = null } = data;
    
    isConnected = connected;
    
    if (connected) {
      statusElement.textContent = '✅ Connected to ChatGPT';
      statusElement.style.color = '#4ade80';
    } else {
      statusElement.textContent = '❌ Not connected to ChatGPT';
      statusElement.style.color = '#f87171';
    }
    
    if (currentInputText && currentInputText.trim()) {
      inputTextElement.textContent = currentInputText;
      inputTextElement.classList.remove('no-input');
      charCountElement.textContent = `${currentInputText.length} characters`;
    } else {
      inputTextElement.innerHTML = '<div class="no-input">No input detected</div>';
      charCountElement.textContent = '0 characters';
    }
    
    if (lastUpdated) {
      const date = new Date(lastUpdated);
      const timeString = date.toLocaleTimeString();
      lastUpdatedElement.textContent = `Last updated: ${timeString}`;
    }
  }
  
  // Function to load data from storage
  function loadData() {
    chrome.storage.local.get(['currentInputText', 'isConnected', 'lastUpdated'], function(data) {
      updateDisplay(data);
    });
  }
  
  // Function to search documents using Flask API
  async function searchDocuments() {
    // Get current input text
    const currentText = inputTextElement.textContent || inputTextElement.innerText || '';
    
    if (!currentText || currentText.trim() === '' || currentText.includes('No input detected')) {
      searchResults.innerHTML = '<div style="color: #ff6b6b; text-align: center; padding: 10px;">❌ No input text to search. Please type something in ChatGPT first.</div>';
      searchResults.style.display = 'block';
      return;
    }
    
    const query = currentText.trim();
    
    // Update button state
    searchBtn.disabled = true;
    searchBtn.textContent = '🔄 Searching...';
    
    // Show loading state
    searchResults.innerHTML = '<div style="text-align: center; padding: 10px;">🔍 Searching documents...</div>';
    searchResults.style.display = 'block';
    
    try {
      const response = await fetch("http://127.0.0.1:5000/search", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          top_k: 3
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      displaySearchResults(data);
      
    } catch (error) {
      console.error('Search error:', error);
      let errorMessage = '❌ Search failed. ';
      
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorMessage += 'Make sure your Flask server is running on localhost:5000';
      } else {
        errorMessage += error.message;
      }
      
      searchResults.innerHTML = `<div style="color: #ff6b6b; text-align: center; padding: 10px;">${errorMessage}</div>`;
    } finally {
      // Reset button state
      searchBtn.disabled = false;
      searchBtn.textContent = '🔍 Search Documents';
    }
  }
  
  // Function to display search results
  function displaySearchResults(data) {
    if (!data.results || data.results.length === 0) {
      searchResults.innerHTML = '<div style="color: #fbbf24; text-align: center; padding: 10px;">🤷‍♂️ No results found</div>';
      return;
    }
    
    let resultsHtml = `<div style="font-size: 12px; margin-bottom: 10px; opacity: 0.8;">Found ${data.results.length} results for: "${data.query}"</div>`;
    
    data.results.forEach((result, index) => {
      const similarity = Math.round(result.similarity * 100);
      const content = result.content.length > 100 ? result.content.substring(0, 100) + '...' : result.content;
      
      resultsHtml += `
        <div class="search-result-item">
          <div class="search-result-header">
            <span class="search-result-key">#${index + 1} ${result.key}</span>
            <span class="search-result-similarity">${similarity}%</span>
          </div>
          <div class="search-result-content">${content}</div>
        </div>
      `;
    });
    
    searchResults.innerHTML = resultsHtml;
  }
  function refreshConnection() {
    refreshBtn.textContent = '🔄 Refreshing...';
    refreshBtn.disabled = true;
    
    // Send message to content script to refresh
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'getInputText' }, function(response) {
          if (chrome.runtime.lastError) {
            console.error('Error sending message:', chrome.runtime.lastError);
            statusElement.textContent = '❌ Error: Please refresh the ChatGPT page';
            statusElement.style.color = '#f87171';
          } else {
            console.log('Refresh message sent successfully');
          }
          
          refreshBtn.textContent = '🔄 Refresh Connection';
          refreshBtn.disabled = false;
          
          // Reload data after refresh
          setTimeout(loadData, 500);
        });
      } else {
        statusElement.textContent = '❌ No active ChatGPT tab found';
        statusElement.style.color = '#f87171';
        refreshBtn.textContent = '🔄 Refresh Connection';
        refreshBtn.disabled = false;
      }
    });
  }
  
  // Event listeners
  refreshBtn.addEventListener('click', refreshConnection);
  
  // Search button event listener
  searchBtn.addEventListener('click', searchDocuments);
  
  // Listen for storage changes
  chrome.storage.onChanged.addListener(function(changes, namespace) {
    if (namespace === 'local') {
      loadData();
    }
  });
  
  // Initial load
  loadData();
  
  // Auto-refresh every 2 seconds
  setInterval(loadData, 2000);
  
  // Check if we're on a ChatGPT page
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    if (tabs[0]) {
      const url = tabs[0].url;
      if (!url.includes('chatgpt.com') && !url.includes('chat.openai.com')) {
        statusElement.textContent = '⚠️ Please navigate to ChatGPT';
        statusElement.style.color = '#fbbf24';
        inputTextElement.innerHTML = '<div class="no-input">Please open ChatGPT in your browser</div>';
      }
    }
  });
});
