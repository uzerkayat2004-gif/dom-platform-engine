/**
 * DOM Platform — Glass Box
 * glassbox.js — Real-time activity log rendering
 */

const GlassBox = {
  entryCount: 0,
  blockedCount: 0,
  passedCount: 0,

  init() {
    // Glass Box is pre-populated with sample entries in HTML
    // This module handles dynamic additions (used in Part 2)
    this.updateStats();
  },

  addEntry(type, message, time = null) {
    const log = document.getElementById('glassbox-log');
    const now = time || new Date().toLocaleTimeString('en-US', { hour12: false });

    const icons = {
      'blocked': '🔴',
      'passed': '✅',
      'assembly': '⚙️',
      'order': '📋',
      'system': '🔧'
    };

    const typeLabels = {
      'blocked': 'BLOCKED',
      'passed': 'PASSED',
      'assembly': 'ASSEMBLY',
      'order': 'ORDER',
      'system': 'SYSTEM'
    };

    const entry = document.createElement('div');
    entry.className = `glassbox-entry ${type}${type === 'blocked' ? ' flash' : ''}`;
    
    // Check if it's a raw entry from DOM server (Fix 8)
    if (message && typeof message === 'object' && message.full_entry) {
        entry.innerHTML = `
          <span class="entry-time">[${now}]</span>
          <span class="entry-icon">${message.is_blocked ? '🔴' : '📋'}</span>
          <span class="entry-type">${message.action_type || 'INFO'}</span>
          <span class="entry-message">${message.full_entry}</span>
        `;
        if (message.is_blocked) type = 'blocked';
    } else {
        entry.innerHTML = `
          <span class="entry-time">[${now}]</span>
          <span class="entry-icon">${icons[type] || '📋'}</span>
          <span class="entry-type">${typeLabels[type] || type.toUpperCase()}</span>
          <span class="entry-message">${message}</span>
        `;
    }

    log.appendChild(entry);
    this.entryCount++;

    if (type === 'blocked') {
      this.blockedCount++;
      // Show notification badge on titlebar icon
      const badge = document.getElementById('glassbox-badge');
      const drawer = document.getElementById('glassbox-drawer');
      if (!drawer.classList.contains('open')) {
        badge.classList.add('show');
      }
    } else if (type === 'passed') {
      this.passedCount++;
    }

    this.updateStats();

    // Auto-scroll
    setTimeout(() => {
      log.scrollTop = log.scrollHeight;
    }, 50);

    // Remove flash class after animation
    if (type === 'blocked') {
      setTimeout(() => {
        entry.classList.remove('flash');
      }, 700);
    }
  },

  updateStats() {
    const stats = document.querySelector('.glassbox-stats');
    if (stats) {
      stats.innerHTML = `
        <span class="glassbox-stat">${this.entryCount} actions logged</span>
        <span class="glassbox-stat blocked-count">${this.blockedCount} blocked</span>
        <span class="glassbox-stat passed-count">${this.passedCount - this.blockedCount + this.entryCount - this.blockedCount > 0 ? this.entryCount - this.blockedCount : 0} passed</span>
      `;
    }
  },
  
  async loadGlassBoxHistory(projectId) {
    if (!projectId) return;
    try {
        const response = await fetch(`${App.apiBase}/glassbox/${projectId}`);
        const data = await response.json();
        // Clear old logs first if any, or just append
        const log = document.getElementById('glassbox-log');
        if (log && data.entries && data.entries.length > 0) {
            log.innerHTML = '';
            this.entryCount = 0;
            this.blockedCount = 0;
            this.passedCount = 0;
            
            data.entries.forEach(entry => this.addEntry(entry.includes('BLOCKED') ? 'blocked' : 'passed', {
                full_entry: entry,
                is_blocked: entry.includes('BLOCKED'),
                action_type: entry.includes('BLOCKED') ? 'SECURITY_BLOCK' : 'INFO'
            }));
        }
    } catch (e) {
        // DOM server not started yet
    }
  }
};
