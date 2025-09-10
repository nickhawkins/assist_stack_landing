// Content script to collect fully rendered HTML
(function() {
  'use strict';

  // Function to scroll page to trigger lazy-loaded content
  function scrollPageForLazyContent() {
    return new Promise((resolve) => {
      let scrollCount = 0;
      const maxScrolls = 3;
      const scrollDelay = 1000; // 1 second between scrolls
      
      function doScroll() {
        if (scrollCount >= maxScrolls) {
          // Scroll back to top
          window.scrollTo(0, 0);
          setTimeout(resolve, 500);
          return;
        }
        
        // Scroll to bottom
        window.scrollTo(0, document.body.scrollHeight);
        scrollCount++;
        
        setTimeout(doScroll, scrollDelay);
      }
      
      doScroll();
    });
  }

  // Function to add base href if it doesn't exist
  function ensureBaseHref() {
    const existingBase = document.querySelector('base[href]');
    if (!existingBase) {
      const baseElement = document.createElement('base');
      baseElement.href = window.location.origin + window.location.pathname;
      
      // Insert at the beginning of head
      const head = document.head;
      if (head.firstChild) {
        head.insertBefore(baseElement, head.firstChild);
      } else {
        head.appendChild(baseElement);
      }
    }
  }

  // Function to collect full HTML with doctype
  function collectFullHTML() {
    // Ensure base href is present
    ensureBaseHref();
    
    // Get the doctype
    let doctypeString = '';
    if (document.doctype) {
      doctypeString = "<!DOCTYPE " + document.doctype.name + ">";
    }
    
    // Get the full HTML
    const fullHTML = doctypeString + document.documentElement.outerHTML;
    
    return fullHTML;
  }

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'collectHTML') {
      // Scroll page to trigger lazy content, then collect HTML
      scrollPageForLazyContent().then(() => {
        const html = collectFullHTML();
        sendResponse({
          success: true,
          html: html,
          url: window.location.href,
          title: document.title
        });
      }).catch((error) => {
        sendResponse({
          success: false,
          error: error.message
        });
      });
      
      // Return true to indicate we'll send a response asynchronously
      return true;
    }
  });
})();