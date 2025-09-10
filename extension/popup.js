// Popup script to handle user interaction and send data to backend
(function() {
  'use strict';
  
  const API_BASE_URL = 'http://localhost:5001';
  
  // DOM elements
  const displayNameInput = document.getElementById('displayName');
  const collectBtn = document.getElementById('collectBtn');
  const statusDiv = document.getElementById('status');
  
  // Utility functions
  function showStatus(message, type = 'loading') {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
  }
  
  function hideStatus() {
    statusDiv.style.display = 'none';
  }
  
  function sanitizeDisplayName(name) {
    // Remove potentially dangerous characters
    return name.replace(/[<>:"\/\\|?*\x00-\x1f]/g, '').trim();
  }
  
  function setButtonState(enabled) {
    collectBtn.disabled = !enabled;
    collectBtn.textContent = enabled ? 'Collect HTML' : 'Processing...';
  }
  
  // Get current tab info
  async function getCurrentTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab;
  }
  
  // Send message to content script
  async function collectHTMLFromPage(tabId) {
    return new Promise((resolve, reject) => {
      chrome.tabs.sendMessage(tabId, { action: 'collectHTML' }, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }
        
        if (response && response.success) {
          resolve(response);
        } else {
          reject(new Error(response?.error || 'Failed to collect HTML'));
        }
      });
    });
  }
  
  // Send data to backend
  async function sendToBackend(data) {
    const response = await fetch(`${API_BASE_URL}/files/create_html`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend error: ${response.status} - ${errorText}`);
    }
    
    return await response.json();
  }
  
  // Main collection function
  async function collectAndSubmit() {
    try {
      setButtonState(false);
      hideStatus();
      
      // Validate input
      const displayName = sanitizeDisplayName(displayNameInput.value);
      if (!displayName) {
        throw new Error('Please enter a display name');
      }
      
      showStatus('Getting current page...', 'loading');
      
      // Get current tab
      const tab = await getCurrentTab();
      if (!tab) {
        throw new Error('No active tab found');
      }
      
      showStatus('Collecting HTML content...', 'loading');
      
      // Collect HTML from content script
      const htmlData = await collectHTMLFromPage(tab.id);
      
      showStatus('Sending to backend...', 'loading');
      
      // Prepare data for backend
      const backendData = {
        display_name: displayName,
        url: htmlData.url,
        html: htmlData.html
      };
      
      // Send to backend
      const result = await sendToBackend(backendData);
      
      showStatus('Successfully submitted!', 'success');
      
      // Clear input and close popup after short delay
      setTimeout(() => {
        displayNameInput.value = '';
        window.close();
      }, 1500);
      
    } catch (error) {
      console.error('Collection error:', error);
      showStatus(`Error: ${error.message}`, 'error');
    } finally {
      setButtonState(true);
    }
  }
  
  // Initialize popup
  async function initialize() {
    try {
      // Get current tab to populate default display name
      const tab = await getCurrentTab();
      if (tab && tab.title) {
        displayNameInput.value = tab.title.substring(0, 50); // Limit length
      }
    } catch (error) {
      console.error('Initialization error:', error);
    }
    
    // Set up event listeners
    collectBtn.addEventListener('click', collectAndSubmit);
    
    // Allow Enter key to submit
    displayNameInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        collectAndSubmit();
      }
    });
    
    // Focus on input
    displayNameInput.focus();
    displayNameInput.select();
  }
  
  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();