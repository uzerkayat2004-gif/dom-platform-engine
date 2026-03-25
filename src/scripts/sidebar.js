/**
 * DOM Platform — Sidebar
 * sidebar.js — Project list, navigation
 */

const Sidebar = {
  init() {
    this.loadRecentProjects();
  },

  bindProjectItems() {
    const projects = document.querySelectorAll('.sidebar-project');

    projects.forEach(project => {
      project.addEventListener('click', () => {
        // Remove active from all
        projects.forEach(p => p.classList.remove('active'));
        project.classList.add('active');

        // Update chat header title and titlebar project name
        const name = project.querySelector('.sidebar-project-name').textContent;
        document.getElementById('chat-project-title').textContent = name;
        document.getElementById('titlebar-project-name').textContent = name;

        // Make this the active project
        const projectId = project.dataset.id;
        App.currentProject = projectId;

        // Transition state if needed
        if (App.state === 'welcome') {
          App.transitionToActive('');
        }

        // ---- Restore chat history for this project ----
        Chat.restoreHistory(projectId);

        // If no history, show a resuming message
        if (Chat.messages.length === 0) {
          Chat.addAIMessage(`Resuming project <strong>${name}</strong>. What would you like to do next?`);
        }
      });
    });
  },

  async loadRecentProjects() {
    // Try backend first, fall back to localStorage index
    try {
      const response = await fetch(`${App.apiBase}/projects`);
      const data = await response.json();
      // Merge with any extra localStorage-only projects
      const merged = this._mergeWithLocalProjects(data.projects || []);
      this.renderProjectList(merged);
    } catch (e) {
      // Backend offline — show projects from localStorage only
      const localProjects = this._getLocalProjects();
      this.renderProjectList(localProjects);
    }
  },

  /**
   * Track project in localStorage so sidebar works offline
   */
  trackProject(projectId, projectName) {
    try {
      const key = 'dom_projects_index';
      const existing = JSON.parse(localStorage.getItem(key) || '[]');
      // Avoid duplicates
      if (!existing.find(p => p.name === projectId)) {
        existing.unshift({
          name: projectId,
          display: projectName,
          created_at: new Date().toISOString()
        });
        localStorage.setItem(key, JSON.stringify(existing.slice(0, 20))); // Keep last 20
      }
    } catch (e) {}
  },

  _getLocalProjects() {
    try {
      return JSON.parse(localStorage.getItem('dom_projects_index') || '[]');
    } catch (e) {
      return [];
    }
  },

  _mergeWithLocalProjects(backendProjects) {
    const localProjects = this._getLocalProjects();
    const backendIds = new Set(backendProjects.map(p => p.name));
    // Add local-only projects that aren't in backend response
    const localOnly = localProjects.filter(p => !backendIds.has(p.name));
    return [...backendProjects, ...localOnly];
  },

  renderProjectList(projects) {
    const list = document.querySelector('.sidebar-section-content');
    if (!list) return;

    list.innerHTML = '';

    if (!projects || projects.length === 0) {
      list.innerHTML = '<div style="padding:10px; opacity:0.6; font-size:12px;">No projects yet — describe your first app above.</div>';
      return;
    }

    projects.forEach(p => {
      const item = document.createElement('div');
      item.className = 'sidebar-project';
      item.dataset.id = p.name;

      let dateStr = '';
      if (p.created_at) {
        const d = new Date(p.created_at);
        const now = new Date();
        const diffMs = now - d;
        const diffHrs = Math.floor(diffMs / 3600000);
        if (diffHrs < 1) dateStr = 'Just now';
        else if (diffHrs < 24) dateStr = `${diffHrs}h ago`;
        else dateStr = d.toLocaleDateString();
      }

      // Show a chat history badge if messages exist
      const historyKey = `dom_chat_${p.name}`;
      let historyBadge = '';
      try {
        const history = JSON.parse(localStorage.getItem(historyKey) || '[]');
        if (history.length > 0) {
          historyBadge = `<span style="font-size:10px;color:var(--blue-400);opacity:0.8;">💬 ${Math.floor(history.length/2)} msgs</span>`;
        }
      } catch (e) {}

      item.innerHTML = `
        <span class="sidebar-project-icon">📂</span>
        <div style="display:flex;flex-direction:column;gap:2px;flex:1;min-width:0;">
          <span class="sidebar-project-name">${p.name.replace(/-/g, ' ').replace(/\b\w/g, c=>c.toUpperCase())}</span>
          <div style="display:flex;gap:6px;align-items:center;">
            <span style="font-size:10px;opacity:0.5;">${dateStr}</span>
            ${historyBadge}
          </div>
        </div>
      `;
      list.appendChild(item);
    });

    this.bindProjectItems();
  }
};
