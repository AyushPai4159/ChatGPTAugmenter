// Popup script for ChatGPT Input Monitor
document.addEventListener('DOMContentLoaded', function() {
  const inputTextElement = document.getElementById('inputText');
  const charCountElement = document.getElementById('charCount');
  const statusElement = document.getElementById('status');
  const refreshBtn = document.getElementById('refreshBtn');
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
  
  // Function to refresh connection
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
