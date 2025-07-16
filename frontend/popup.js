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
    integrateBackend(query)
    
    
  }
  async function integrateBackend(query) {
     try {
      const response = await fetch("http://127.0.0.1:5000/search", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          top_k: 6
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
    
    const popupWindow = window.open('', 'SearchResults', 'width=800,height=600,resizable=yes,scrollbars=yes');
    
    if (!popupWindow) {
      searchResults.innerHTML = '<div style="color: #ff6b6b; text-align: center; padding: 10px;">❌ Popup blocked. Please allow popups for this extension.</div>';
      searchResults.style.display = 'block';
      return;
    }

    if (!data.results || data.results.length === 0) {
      popupWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Search Results</title>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
              margin: 0;
              padding: 20px;
              min-height: 100vh;
            }
            .no-results {
              text-align: center;
              padding: 40px;
              font-size: 18px;
            }
          </style>
        </head>
        <body>
          <div class="no-results">🤷‍♂️ No results found for "${data.query}"</div>
        </body>
        </html>
      `);
      popupWindow.document.close();
      return;
    }
    
    // Function to convert markdown to HTML
    function parseMarkdown(text) {
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
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
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
    }
    
    let htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Search Results - ${data.query}</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
          }
          
          .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
          }
          
          .header h1 {
            margin: 0 0 10px 0;
            font-size: 24px;
            font-weight: 600;
          }
          
          .query-info {
            font-size: 14px;
            opacity: 0.8;
          }
          
          .result-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
          }
          
          .result-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.15);
          }
          
          .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          }
          
          .result-title {
            font-size: 18px;
            font-weight: 600;
            color: #fff;
          }
          
          .similarity-badge {
            background: rgba(255, 255, 255, 0.3);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
          }
          
          .result-content {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 10px;
            line-height: 1.7;
            max-height: 300px;
            overflow-y: auto;
          }
          
          .result-content h1, .result-content h2, .result-content h3 {
            color: #fff;
            margin-top: 20px;
            margin-bottom: 10px;
          }
          
          .result-content h1 { font-size: 20px; }
          .result-content h2 { font-size: 18px; }
          .result-content h3 { font-size: 16px; }
          
          .result-content p {
            margin: 10px 0;
          }
          
          .result-content code {
            background: rgba(255, 255, 255, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
          }
          
          .result-content pre {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
          }
          
          .result-content pre code {
            background: none;
            padding: 0;
            border-radius: 0;
          }
          
          .result-content strong {
            color: #fff;
            font-weight: 600;
          }
          
          .result-content em {
            color: #e2e8f0;
            font-style: italic;
          }
          
          .result-content ul, .result-content ol {
            margin: 10px 0;
            padding-left: 20px;
          }
          
          .result-content li {
            margin: 5px 0;
          }
          
          .result-content a {
            color: #93c5fd;
            text-decoration: none;
          }
          
          .result-content a:hover {
            text-decoration: underline;
          }
          
          .result-content blockquote {
            border-left: 4px solid rgba(255, 255, 255, 0.3);
            margin: 15px 0;
            padding-left: 15px;
            font-style: italic;
            opacity: 0.9;
          }
          
          .footer {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            opacity: 0.7;
            font-size: 12px;
          }
          
          ::-webkit-scrollbar {
            width: 8px;
          }
          
          ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
          }
          
          ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 4px;
          }
          
          ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.5);
          }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>🔍 Search Results</h1>
          <div class="query-info">Query: "<strong>${data.query}</strong>" | Found ${data.results.length} results</div>
        </div>
    `;
    
    data.results.forEach((result, index) => {
      const similarity = Math.round(result.similarity * 100);
      const parsedContent = parseMarkdown(result.content);
      
      htmlContent += `
        <div class="result-card">
          <div class="result-header">
            <div class="result-title">#${index + 1} ${result.key}</div>
            <div class="similarity-badge">${similarity}% match</div>
          </div>
          <div class="result-content">${parsedContent}</div>
        </div>
      `;
    });
    
    htmlContent += `
        <div class="footer">
          Powered by Semantic Search Extension
        </div>
      </body>
      </html>
    `;
    
    popupWindow.document.write(htmlContent);
    popupWindow.document.close();
    popupWindow.focus();
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



