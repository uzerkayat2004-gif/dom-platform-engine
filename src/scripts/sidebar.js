/**
 * DOM Platform — Sidebar
 * sidebar.js — Project list, navigation
 */

const Sidebar = {
  init() {
    this.bindProjectItems();
  },

  bindProjectItems() {
    const projects = document.querySelectorAll('.sidebar-project');

    projects.forEach(project => {
      project.addEventListener('click', () => {
        // Remove active from all
        projects.forEach(p => p.classList.remove('active'));
        // Set clicked as active
        project.classList.add('active');

        // Update chat header title and titlebar project name
        const name = project.querySelector('.sidebar-project-name').textContent;
        document.getElementById('chat-project-title').textContent = name;
        document.getElementById('titlebar-project-name').textContent = name;
        
        // Make this the active project
        App.currentProject = project.dataset.id;
        
        // Transition state if needed
        if (App.state === 'welcome') {
          App.transitionToActive("Resuming project");
        }
      });
    });
  },
  
  async loadRecentProjects() {
    try {
        const response = await fetch('http://127.0.0.1:8080/projects');
        const data = await response.json();
        this.renderProjectList(data.projects);
    } catch (e) {
        this.renderProjectList([]);
    }
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
      item.innerHTML = `
        <span class="sidebar-project-icon">📂</span>
        <span class="sidebar-project-name">${p.name.replace('-', ' ').replace(/\b\w/g, c=>c.toUpperCase())}</span>
      `;
      list.appendChild(item);
    });
    
    this.bindProjectItems();
  }
};
