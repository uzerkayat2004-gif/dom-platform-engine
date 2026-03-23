/**
 * DOM Platform — Activity Status Bar
 * activity.js — Shows real-time feedback so the user always knows DOM is working
 */

const Activity = {
  timer: null,
  startTime: null,
  
  init() {
    // Nothing to bind — show/hide controlled programmatically
  },

  /**
   * Show the activity bar with a status message
   * @param {string} text - Main status text (e.g. "DOM is thinking...")
   * @param {string} step - Current step description (optional)
   */
  show(text, step = '') {
    const bar = document.getElementById('activity-bar');
    const textEl = document.getElementById('activity-text');
    const stepEl = document.getElementById('activity-step');
    
    if (!bar) return;
    
    bar.style.display = 'flex';
    if (textEl) textEl.textContent = text;
    if (stepEl) stepEl.textContent = step ? `— ${step}` : '';
    
    // Start elapsed timer if not already running
    if (!this.timer) {
      this.startTime = Date.now();
      this.timer = setInterval(() => this.updateTimer(), 1000);
      this.updateTimer();
    }
  },

  /**
   * Update just the step text without resetting the timer
   */
  updateStep(step) {
    const stepEl = document.getElementById('activity-step');
    if (stepEl) stepEl.textContent = step ? `— ${step}` : '';
  },

  /**
   * Update the elapsed time display
   */
  updateTimer() {
    const timerEl = document.getElementById('activity-timer');
    if (!timerEl || !this.startTime) return;
    
    const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
    const mins = Math.floor(elapsed / 60);
    const secs = elapsed % 60;
    
    if (mins > 0) {
      timerEl.textContent = `${mins}m ${secs.toString().padStart(2, '0')}s`;
    } else {
      timerEl.textContent = `${secs}s`;
    }
  },

  /**
   * Hide the activity bar and reset timer
   */
  hide() {
    const bar = document.getElementById('activity-bar');
    if (bar) bar.style.display = 'none';
    
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
      this.startTime = null;
    }
    
    const timerEl = document.getElementById('activity-timer');
    if (timerEl) timerEl.textContent = '';
  },

  /**
   * Convenience: show "DOM is thinking..." (for chat responses)
   */
  thinking() {
    this.show('DOM is thinking...', 'Processing your message');
  },

  /**
   * Convenience: show "Generating rules..." 
   */
  generatingRules() {
    this.show('DOM is generating rules...', 'Creating constitutional rule files');
  },

  /**
   * Convenience: show training status
   */
  training(step = '') {
    this.show('DOM is training your AI model...', step || 'Fine-tuning in progress');
  },

  /**
   * Convenience: show building frontend status
   */
  buildingFrontend() {
    this.show('DOM is building your app...', 'Generating frontend code');
  },

  /**
   * Convenience: show completed (briefly, then hide)
   */
  complete(message = 'Done!') {
    const bar = document.getElementById('activity-bar');
    const textEl = document.getElementById('activity-text');
    const stepEl = document.getElementById('activity-step');
    const pulse = bar?.querySelector('.activity-pulse');
    
    if (textEl) textEl.textContent = `✓ ${message}`;
    if (stepEl) stepEl.textContent = '';
    if (pulse) {
      pulse.style.background = 'var(--success)';
      pulse.style.boxShadow = '0 0 12px var(--success)';
    }
    
    // Stop timer but keep it visible briefly
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    
    // Hide after 3 seconds
    setTimeout(() => {
      this.hide();
      if (pulse) {
        pulse.style.background = '';
        pulse.style.boxShadow = '';
      }
    }, 3000);
  }
};
