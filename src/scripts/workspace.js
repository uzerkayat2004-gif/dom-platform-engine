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
        
        // Auto-load data when switching to Rules tab
        if (tabName === 'rules' && App.currentProject) {
          this.loadRuleFiles(App.currentProject);
        }
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
        const response = await fetch(`http://127.0.0.1:8080/project-files/${projectId}`);
        const data = await response.json();
        const tree = document.getElementById('file-tree');
        if (!tree) return;
        
        tree.innerHTML = '';
        
        // Project root
        tree.innerHTML += `<div class="file-tree-item">
          <span class="tree-indent"></span>
          <span class="tree-icon">📁</span>
          <span class="tree-name">${projectId}/</span>
        </div>`;
        
        if (data.files && data.files.length > 0) {
            data.files.forEach(f => {
                tree.innerHTML += `<div class="file-tree-item">
                  <span class="tree-indent">  ├── </span>
                  <span class="tree-icon">📄</span>
                  <span class="tree-name">${f.name}</span>
                  <span class="tree-status done">✅ Generated</span>
                </div>`;
            });
        } else {
            tree.innerHTML += `<div class="file-tree-item">
              <span class="tree-indent">  </span>
              <span class="tree-name" style="opacity:0.5">No files yet...</span>
            </div>`;
        }
    } catch (e) {
        console.log('File tree refresh failed:', e);
    }
  },
  
  addFile(filename) {
    const tree = document.getElementById('file-tree');
    if (!tree) return;
    const item = document.createElement('div');
    item.className = 'file-tree-item';
    item.innerHTML = `
      <span class="tree-indent">  ├── </span>
      <span class="tree-icon">📄</span>
      <span class="tree-name">${filename}</span>
      <span class="tree-status done">✅ Generated</span>
    `;
    tree.appendChild(item);
  },
  
  async loadRuleFiles(projectId) {
    if (!projectId) return;
    const files = ['security.md', 'behavior.md', 'limits.md', 'skills.md'];
    const container = document.getElementById('workspace-rules-container');
    if (!container) return;
    container.innerHTML = '';
    
    for (const file of files) {
        try {
            const r = await fetch(`http://127.0.0.1:8080/rule-file/${projectId}/${file}`);
            const data = await r.json();
            
            const icons = {'security.md': '🔒', 'behavior.md': '⚙️', 'limits.md': '🚫', 'skills.md': '✅'};
            const card = document.createElement('div');
            card.className = 'rule-file-card';
            card.innerHTML = `
              <div class="rule-file-header" data-rule="${file.replace('.md','')}">
                <span class="rule-file-title">${icons[file] || '📋'} ${file}</span>
                <span class="rule-file-toggle">▼</span>
              </div>
              <div class="rule-file-content">${data.content || 'Not generated yet'}</div>
            `;
            container.appendChild(card);
        } catch (e) {
            console.error(`Failed to load ${file}:`, e);
        }
    }
    
    // Re-bind click handlers for new cards
    this.bindRuleFileCards();
  },
  
  switchTab(tabName) {
    const tabs = document.querySelectorAll('.workspace-tab');
    const views = {
      'building': 'view-building',
      'preview': 'view-preview',
      'rules': 'view-rules',
      'code': 'view-code'
    };
    tabs.forEach(t => {
      t.classList.toggle('active', t.dataset.tab === tabName);
    });
    Object.entries(views).forEach(([key, viewId]) => {
      document.getElementById(viewId).classList.toggle('active', key === tabName);
    });
    this.activeTab = tabName;
  }
};
