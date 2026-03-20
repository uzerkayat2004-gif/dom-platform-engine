/**
 * DOM Platform — App Controller
 * app.js — Initialization, state management, panel routing
 */

const App = {
  state: 'welcome', // 'welcome' | 'active'
  currentProject: null,
  config: { provider: 'groq', apiKey: '' },
  apiBase: 'http://127.0.0.1:8080',
  ws: null,

  init() {
    this.bindWindowControls();
    this.bindStateTransitions();
    this.bindGlassBox();
    this.bindSettings();
    this.bindKeyboard();

    // Initialize sub-modules
    Sidebar.init();
    Chat.init();
    Workspace.init();
    GlassBox.init();
    Editor.init();
    Deploy.init();
    ModelSelector.init();
  },

  // ---- Window Controls (Tauri) ----
  bindWindowControls() {
    const minimize = document.getElementById('btn-minimize');
    const maximize = document.getElementById('btn-maximize');
    const close = document.getElementById('btn-close');

    minimize.addEventListener('click', async (e) => {
      e.stopPropagation();
      try {
        if (window.__TAURI__) {
          await window.__TAURI__.core.invoke('minimize_window');
        }
      } catch (err) { console.log('Minimize:', err); }
    });

    maximize.addEventListener('click', async (e) => {
      e.stopPropagation();
      try {
        if (window.__TAURI__) {
          await window.__TAURI__.core.invoke('maximize_window');
        }
      } catch (err) { console.log('Maximize:', err); }
    });

    close.addEventListener('click', async (e) => {
      e.stopPropagation();
      try {
        if (window.__TAURI__) {
          await window.__TAURI__.core.invoke('close_window');
        }
      } catch (err) { console.log('Close:', err); }
    });
  },

  // ---- State Transitions ----
  bindStateTransitions() {
    // Build It button
    const buildBtn = document.getElementById('btn-build-it');
    buildBtn.addEventListener('click', () => {
      const input = document.getElementById('welcome-input');
      const text = input.value.trim();
      if (text) {
        this.createProject("My App", text).then(() => {
          this.transitionToActive(text);
        });
      }
    });

    // Welcome textarea — Enter to submit (without Shift)
    const welcomeInput = document.getElementById('welcome-input');
    welcomeInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        buildBtn.click();
      }
    });

    // Back button in chat
    const backBtn = document.getElementById('btn-chat-back');
    backBtn.addEventListener('click', () => {
      this.transitionToWelcome();
    });

    // New Generation button
    const newGenBtn = document.getElementById('btn-new-generation');
    newGenBtn.addEventListener('click', () => {
      if (this.state === 'welcome') {
        // Focus the input
        document.getElementById('welcome-input').focus();
      } else {
        // Reset and go to welcome with fresh state
        this.transitionToWelcome();
        setTimeout(() => {
          document.getElementById('welcome-input').value = '';
          document.getElementById('welcome-input').focus();
        }, 450);
      }
    });
  },

  transitionToActive(initialMessage) {
    const app = document.getElementById('app');
    const welcomeCenter = document.getElementById('welcome-center');
    const chatPanel = document.getElementById('chat-panel');
    const workspacePanel = document.getElementById('workspace-panel');
    const titleProjectName = document.getElementById('titlebar-project-name');

    // Animate out welcome
    welcomeCenter.classList.add('animate-fade-out-up');

    setTimeout(() => {
      app.classList.remove('state-welcome');
      app.classList.add('state-active');
      welcomeCenter.classList.remove('animate-fade-out-up');

      // Animate in panels
      chatPanel.classList.add('animate-slide-in-left');
      workspacePanel.classList.add('animate-fade-in');

      // Show project name in titlebar
      titleProjectName.classList.add('visible');

      // Set state
      this.state = 'active';

      // Initial User Message is handled by transitionToActive caller,
      // but let's actually send it to the engine now:
      this.sendChatMessage(initialMessage);

      // Clean up animation classes after they complete
      setTimeout(() => {
        chatPanel.classList.remove('animate-slide-in-left');
        workspacePanel.classList.remove('animate-fade-in');
      }, 450);
    }, 200);
  },

  transitionToWelcome() {
    const app = document.getElementById('app');
    const titleProjectName = document.getElementById('titlebar-project-name');

    app.classList.remove('state-active');
    app.classList.add('state-welcome');

    // Hide project name in titlebar
    titleProjectName.classList.remove('visible');

    // Reset welcome center
    const welcomeCenter = document.getElementById('welcome-center');
    welcomeCenter.classList.add('animate-fade-in-up');
    setTimeout(() => {
      welcomeCenter.classList.remove('animate-fade-in-up');
    }, 450);

    this.state = 'welcome';
  },

  // ---- Glass Box Drawer ----
  bindGlassBox() {
    const toggleBtn = document.getElementById('btn-glassbox-toggle');
    const drawer = document.getElementById('glassbox-drawer');

    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = drawer.classList.contains('open');

      if (isOpen) {
        drawer.classList.remove('open');
        toggleBtn.classList.remove('active');
      } else {
        // Close settings if open
        this.closeSettings();
        drawer.classList.add('open');
        toggleBtn.classList.add('active');

        // Fix 8: Real Data
        if (this.currentProject) {
            GlassBox.loadGlassBoxHistory(this.currentProject);
        }

        // Clear notification badge
        const badge = document.getElementById('glassbox-badge');
        badge.classList.remove('show');
      }
    });
  },

  // ---- Settings Panel ----
  bindSettings() {
    const settingsBtn = document.getElementById('btn-settings');
    const modelStatusBtn = document.getElementById('btn-model-status');
    const closeBtn = document.getElementById('btn-settings-close');
    const overlay = document.getElementById('settings-overlay');

    const openSettings = () => {
      // Close glass box if open
      document.getElementById('glassbox-drawer').classList.remove('open');
      document.getElementById('btn-glassbox-toggle').classList.remove('active');

      document.getElementById('settings-panel').classList.add('open');
      overlay.classList.add('visible');
    };

    settingsBtn.addEventListener('click', openSettings);
    modelStatusBtn.addEventListener('click', openSettings);
    closeBtn.addEventListener('click', () => this.closeSettings());
    overlay.addEventListener('click', () => this.closeSettings());
  },

  closeSettings() {
    document.getElementById('settings-panel').classList.remove('open');
    document.getElementById('settings-overlay').classList.remove('visible');
  },

  // ---- Keyboard Shortcuts ----
  bindKeyboard() {
    document.addEventListener('keydown', (e) => {
      // Escape closes drawers/panels
      if (e.key === 'Escape') {
        this.closeSettings();
        document.getElementById('glassbox-drawer').classList.remove('open');
        document.getElementById('btn-glassbox-toggle').classList.remove('active');
      }
    });
  },

  // ---- Engine Communication ----
  connectWebSocket() {
    if (this.ws) this.ws.close();
    try {
      this.ws = new WebSocket('ws://127.0.0.1:8080/ws');
      this.ws.onopen = () => console.log('Connected to DOM Engine WS');
      this.ws.onmessage = (e) => this.handleEngineMessage(JSON.parse(e.data));
      this.ws.onclose = () => setTimeout(() => this.connectWebSocket(), 3000);
    } catch (err) {
      console.error('WS Error:', err);
    }
  },

  handleEngineMessage(data) {
    if (data.project_id && data.project_id !== this.currentProject) return;
    
    switch (data.type) {
      case 'status':
        if (data.status === 'thinking' || data.status === 'generating_rules') {
           Chat.showTyping();
        } else {
           Chat.hideTyping();
        }
        break;
      case 'file_created':
        Workspace.addFile(data.filename);
        break;
      case 'glass_box_entry':
        GlassBox.addEntry(data.entry);
        break;
      case 'training_progress':
        updateWorkspaceMessage(data.message);
        GlassBox.addEntry({
          action_type: 'SYSTEM',
          type_label: '🔧 SYSTEM',
          message: data.message,
          timestamp: new Date().toLocaleTimeString('en-US', {hour12: false}),
          is_blocked: false,
          full_entry: `[${new Date().toLocaleTimeString('en-US', {hour12: false})}] 🔧 SYSTEM  ${data.message}`
        });
        break;
      case 'training_complete':
        updateWorkspaceMessage('DOM model training complete — building your app...');
        showNotification('Training complete! Building frontend...', 'success');
        break;
      case 'frontend_ready':
        loadAppPreview(data.project_id);
        break;
      case 'app_ready':
        switchWorkspaceToPreview(data.project_id);
        showNotification('Your app is ready!', 'success');
        break;
      case 'workspace_update':
        // Optional: update UI based on step (questioning, etc)
        break;
    }
  },

  async createProject(name, description) {
    try {
      const res = await fetch(`${this.apiBase}/project/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.replace(/\\s+/g, '-').toLowerCase(), description })
      });
      const data = await res.json();
      if (data.success) {
        this.currentProject = data.project_id;
        document.getElementById('titlebar-project-name').textContent = name;
        return true;
      }
    } catch (err) {
      console.error('Create project failed:', err);
    }
    return false;
  },

  async sendChatMessage(message) {
    const provider = this.getSavedProvider();
    const apiKey = this.getSavedApiKey();
    
    if (!apiKey || apiKey.trim() === '') {
        showNotification('Please add your API key in Settings first', 'error');
        Chat.addUserMessage(message);
        Chat.addAIMessage("Authentication Error: Please open Settings and add your API key.");
        return;
    }
    
    if (!this.currentProject) {
        this.currentProject = 'project-' + Date.now();
    }
    
    Chat.addUserMessage(message);
    Chat.showTyping();
    
    try {
        const response = await fetch(`${this.apiBase}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                project_id: this.currentProject,
                message: message,
                provider: provider,
                api_key: apiKey
            })
        });
        const data = await response.json();
        
        Chat.hideTyping();
        Chat.addAIMessage(data.response);
        
        if (data.next_action === 'start_training') {
            this.startTraining();
        }
    } catch (e) {
        Chat.hideTyping();
        Chat.addAIMessage('Engine not reachable. Make sure python scripts/dev.py is running.');
    }
  },

  async startTraining() {
    if (!this.currentProject) return;
    try {
      await fetch(`${this.apiBase}/train/${this.currentProject}`, { method: 'POST' });
    } catch (err) {
      console.error('Training start failed:', err);
    }
  },

  async testApiKey(provider, key) {
    try {
      const res = await fetch(`${this.apiBase}/api-key/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: key })
      });
      const data = await res.json();
      return data.valid;
    } catch (err) {
      return false;
    }
  },
  
  saveApiKey(provider, apiKey) {
    localStorage.setItem(`dom_api_key_${provider}`, apiKey);
    localStorage.setItem('dom_provider', provider);
    this.config.provider = provider;
    this.config.apiKey = apiKey;
  },

  getSavedApiKey() {
    const provider = localStorage.getItem('dom_provider') || 'groq';
    return localStorage.getItem(`dom_api_key_${provider}`) || '';
  },

  getSavedProvider() {
    return localStorage.getItem('dom_provider') || 'groq';
  }
};

async function loadAppPreview(projectId) {
  const response = await fetch(`${App.apiBase}/frontend/${projectId}`);
  const data = await response.json();
  if (data.html) {
      const iframe = document.getElementById('preview-iframe');
      if (iframe) {
          iframe.srcdoc = data.html;
          Workspace.switchTab('preview');
      }
  }
}

function switchWorkspaceToPreview(projectId) {
  // Switch workspace from building state to preview state
  const buildingState = document.getElementById('workspace-building');
  const previewState = document.getElementById('workspace-preview');
  if (buildingState) buildingState.style.display = 'none';
  if (previewState) previewState.style.display = 'flex';
  loadAppPreview(projectId);
}

function updateWorkspaceMessage(message) {
  const statusEl = document.getElementById('workspace-status-message');
  if (statusEl) statusEl.textContent = message;
  Workspace.addFile(message); // Abusing addFile as a message log temporarily for UI parity
}

function showNotification(message, type = 'info') {
  const notif = document.createElement('div');
  notif.className = `notification notification-${type}`;
  notif.textContent = message;
  notif.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: ${type === 'success' ? 'var(--success)' : 'var(--danger)'};
      color: white;
      padding: 12px 20px;
      border-radius: var(--radius-md);
      font-size: 14px;
      z-index: 9999;
      animation: slideInRight 0.3s ease;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  `;
  document.body.appendChild(notif);
  setTimeout(() => notif.remove(), 4000);
}

// Fix 10 — Startup Sequence
async function onAppStart() {
  App.init();
  
  // Load saved settings
  const savedProvider = App.getSavedProvider();
  const savedKey = App.getSavedApiKey();
  const selector = document.getElementById('settings-model-provider');
  const inputKey = document.getElementById('settings-api-key');
  if (selector) selector.value = savedProvider;
  if (inputKey) inputKey.value = savedKey;
  
  // Start 10s health check interval
  await ModelSelector.checkEngineStatus();
  setInterval(() => ModelSelector.checkEngineStatus(), 10000);
  
  await Sidebar.loadRecentProjects();
  App.connectWebSocket();
  
  // Fix 7 - Poll file tree while building
  setInterval(() => {
      if (App.currentProject && Workspace.activeTab === 'building') {
          Workspace.refreshFileTree(App.currentProject);
      }
  }, 3000);
  
  const lastProject = localStorage.getItem('dom_last_project');
  if (lastProject) {
      App.currentProject = lastProject;
      // Load preview if exists
      loadAppPreview(lastProject);
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', onAppStart);
