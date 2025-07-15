// Content script that monitors ChatGPT input field
(function() {
  'use strict';
  
  let lastInputText = '';
  let inputElement = null;
  let observer = null;
  
  // Function to find the input element
  function findInputElement() {
    // ChatGPT uses different selectors, try multiple approaches
    const selectors = [
      'textarea[placeholder*="Message"]',
      'textarea[data-id="root"]',
      'div[contenteditable="true"]',
      'textarea[placeholder*="Send a message"]',
      'div[contenteditable="true"][data-testid*="textbox"]',
      '#prompt-textarea',
      'textarea'
    ];
    

    //look for id #prompt-textarea
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element && (element.tagName === 'TEXTAREA' || element.contentEditable === 'true')) {
        return element;
      }
    }
    
    // // Fallback: look for any textarea or contenteditable div that might be the input
    // const textareas = document.querySelectorAll('textarea');
    // for (const textarea of textareas) {
    //   const rect = textarea.getBoundingClientRect();
    //   if (rect.width > 100 && rect.height > 30) { // Reasonable size for input
    //     return textarea;
    //   }
    // }
    
    // const editableDivs = document.querySelectorAll('div[contenteditable="true"]');
    // for (const div of editableDivs) {
    //   const rect = div.getBoundingClientRect();
    //   if (rect.width > 100 && rect.height > 30) {
    //     return div;
    //   }
    // }
    
    return null;
  }
  
  // Function to get text content from element
  function getElementText(element) {
    if (!element) return '';
    
    if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
      return element.value || '';
    } else if (element.contentEditable === 'true') {
      return element.textContent || element.innerText || '';
    }
    
    return '';
  }
  
  // Function to update stored input text
  function updateInputText() {
    if (!inputElement) {
      inputElement = findInputElement();
    }
    
    if (inputElement) {
      const currentText = getElementText(inputElement);
      
      if (currentText !== lastInputText) {
        lastInputText = currentText;
        
        // Store in chrome storage for popup to access
        chrome.storage.local.set({
          currentInputText: currentText,
          lastUpdated: new Date().toISOString(),
          isConnected: true
        });
        
        console.log('ChatGPT Input Monitor: Text updated', currentText.length, 'characters');
      }
    } else {
      // If no input element found, mark as disconnected
      chrome.storage.local.set({
        isConnected: false,
        lastUpdated: new Date().toISOString()
      });
    }
  }
  
  // Function to start monitoring
  function startMonitoring() {
    console.log('ChatGPT Input Monitor: Starting to monitor input');
    
    // Initial check
    updateInputText();
    
    // Set up interval to check for input changes
    setInterval(updateInputText, 500); // Check every 500ms
    
    // Set up mutation observer to detect DOM changes
    observer = new MutationObserver((mutations) => {
      let shouldRecheck = false;
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' || mutation.type === 'attributes') {
          shouldRecheck = true;
        }
      });
      
      if (shouldRecheck) {
        // Reset input element to trigger re-finding
        inputElement = null;
        updateInputText();
      }
    });
    
    // Observe the document for changes
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['contenteditable', 'placeholder']
    });
    
    // Listen for input events on the document
    document.addEventListener('input', (event) => {
      if (event.target === inputElement || 
          event.target.tagName === 'TEXTAREA' || 
          event.target.contentEditable === 'true') {
        updateInputText();
      }
    }, true);
    
    // Listen for keyup events as well
    document.addEventListener('keyup', (event) => {
      if (event.target === inputElement || 
          event.target.tagName === 'TEXTAREA' || 
          event.target.contentEditable === 'true') {
        updateInputText();
      }
    }, true);
  }
  
  // Wait for the page to load, then start monitoring
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(startMonitoring, 1000); // Give ChatGPT time to load
    });
  } else {
    setTimeout(startMonitoring, 1000);
  }
  
  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getInputText') {
      inputElement = null; // Force re-finding of input element
      updateInputText();
      sendResponse({ success: true });
    }
  });
  
  console.log('ChatGPT Input Monitor: Content script loaded');
})();
