/**
 * DOM Platform — Workspace Panel
 * workspace.js — Tabs, file tree, preview, rule viewer
 */

const Workspace = {
  activeTab: 'building',

  init() {
    this.bindTabs();
    this.bindRuleFileCards();
  },

  bindTabs() {
    const tabs = document.querySelectorAll('.workspace-tab');
    const views = {
      'building': 'view-building',
      'preview': 'view-preview',
      'rules': 'view-rules',
      'code': 'view-code'
    };

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        if (tabName === this.activeTab) return;

        // Update active tab
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update active view
        Object.values(views).forEach(viewId => {
          document.getElementById(viewId).classList.remove('active');
        });
        document.getElementById(views[tabName]).classList.add('active');

        this.activeTab = tabName;
      });
    });
  },

  bindRuleFileCards() {
    const headers = document.querySelectorAll('.rule-file-header');
    
    headers.forEach(header => {
      header.addEventListener('click', () => {
        const card = header.parentElement;
        const content = card.querySelector('.rule-file-content');
        const toggle = header.querySelector('.rule-file-toggle');

        const isExpanded = content.classList.contains('expanded');

        if (isExpanded) {
          content.classList.remove('expanded');
          toggle.classList.remove('expanded');
        } else {
          content.classList.add('expanded');
          toggle.classList.add('expanded');
        }
      });
    });
  },

  // Public methods for dynamic updates (used by engine in Part 2)
  setFileStatus(filename, status) {
    // status: 'done' | 'in-progress' | 'pending'
    const items = document.querySelectorAll('.file-tree-item');
    items.forEach(item => {
      const name = item.querySelector('.tree-name');
      if (name && name.textContent.trim() === filename) {
        const statusEl = item.querySelector('.tree-status');
        if (statusEl) {
          statusEl.className = `tree-status ${status}`;
          if (status === 'done') {
            statusEl.innerHTML = '✅ Generated';
          } else if (status === 'in-progress') {
            statusEl.innerHTML = '<span class="spinner"></span> Generating...';
          } else {
            statusEl.textContent = '(pending)';
          }
        }
      }
    });
  },

  setProgressWidth(percent) {
    const fill = document.getElementById('progress-bar-fill');
    if (fill) {
      fill.style.width = percent + '%';
    }
  },

  setBuildingStep(text) {
    const el = document.getElementById('building-step-text');
    if (el) {
      el.textContent = text;
    }
  },
  
  async refreshFileTree(projectId) {
    if (!projectId) return;
    try {
        const response = await fetch(`http://127.0.0.1:8080/project/${projectId}`);
        const config = await response.json();
        // Since the files shown initially are rules, we can fetch real config or check if rule files exist
        if (config && config.step) {
           // We can map config status to the tree, or if Python engine has an endpoint returning files, use that.
        }
    } catch (e) {
        console.log('File tree refresh failed');
    }
  }
};
