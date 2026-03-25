/**
 * DOM Platform — App Controller
 * app.js — Initialization, state management, panel routing
 */

const App = {
  state: 'welcome', // 'welcome' | 'active'
  currentProject: null,
  config: { provider: 'groq', apiKey: '' },
  apiBase: window.DOM_ENGINE_URL || 'http://127.0.0.1:8080',
  ws: null,

  init() {
    // #region agent log
    debugLogViaTauri('app.js:App.init:entry', 'App.init started', {}, 'pre-fix', 'H13');
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H13',location:'app.js:App.init:entry',message:'App.init started',data:{},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    this.bindWindowControls();
    this.bindStateTransitions();
    this.bindGlassBox();
    this.bindSettings();
    this.bindKeyboard();

    // Initialize sub-modules
    try {
      Sidebar.init();
      Chat.init();
      Workspace.init();
      GlassBox.init();
      Editor.init();
      Deploy.init();
      ModelSelector.init();
      Activity.init();
      // #region agent log
      debugLogViaTauri('app.js:App.init:submodules', 'All submodules initialized', {}, 'pre-fix', 'H13');
      fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H13',location:'app.js:App.init:submodules',message:'All submodules initialized',data:{},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
    } catch (error) {
      // #region agent log
      debugLogViaTauri('app.js:App.init:submodules:catch', 'Submodule initialization failed', { errorMessage: error?.message || 'unknown' }, 'pre-fix', 'H13');
      fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H13',location:'app.js:App.init:submodules:catch',message:'Submodule initialization failed',data:{errorMessage:error?.message||'unknown'},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      throw error;
    }
    // #region agent log
    debugLogViaTauri('app.js:App.init:exit', 'App.init completed', {}, 'pre-fix', 'H13');
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H13',location:'app.js:App.init:exit',message:'App.init completed',data:{},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
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
      // #region agent log
      debugLogViaTauri('app.js:bindStateTransitions:buildClick', 'Build button clicked', { textLength: text.length }, 'pre-fix', 'H10');
      fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H10',location:'app.js:bindStateTransitions:buildClick',message:'Build button clicked',data:{textLength:text.length},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      if (text && !buildBtn.disabled) {
        buildBtn.disabled = true; // Prevent double-click
        this.createProject("My App", text).then(() => {
          // #region agent log
          debugLogViaTauri('app.js:bindStateTransitions:createProjectResolved', 'createProject promise resolved', { hasCurrentProject: !!this.currentProject }, 'pre-fix', 'H10');
          fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H10',location:'app.js:bindStateTransitions:createProjectResolved',message:'createProject promise resolved',data:{hasCurrentProject:!!this.currentProject},timestamp:Date.now()})}).catch(()=>{});
          // #endregion
          this.transitionToActive(text);
          buildBtn.disabled = false;
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
    // #region agent log
    debugLogViaTauri('app.js:transitionToActive:entry', 'Transition to active started', { initialMessageLength: (initialMessage || '').length }, 'pre-fix', 'H11');
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H11',location:'app.js:transitionToActive:entry',message:'Transition to active started',data:{initialMessageLength:(initialMessage||'').length},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
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
      const wsUrl = this.apiBase.replace(/^http/, 'ws') + '/ws';
      this.ws = new WebSocket(wsUrl);
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
        if (data.status === 'thinking') {
           Chat.showTyping();
           Activity.thinking();
        } else if (data.status === 'generating_rules') {
           Chat.showTyping();
           Activity.generatingRules();
        } else if (data.status === 'building_frontend') {
           Activity.buildingFrontend();
        } else {
           Chat.hideTyping();
        }
        break;
      case 'file_created':
        Workspace.addFile(data.filename);
        Activity.updateStep(`Created ${data.filename}`);
        break;
      case 'glass_box_entry':
        GlassBox.addEntry(data.entry);
        break;
      case 'training_progress':
        updateWorkspaceMessage(data.message);
        Activity.training(data.message);
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
        Activity.complete('Training complete!');
        break;
      case 'frontend_ready':
        loadAppPreview(data.project_id);
        break;
      case 'app_ready':
        switchWorkspaceToPreview(data.project_id);
        showNotification('Your app is ready!', 'success');
        Activity.complete('Your app is ready!');
        break;
      case 'workspace_update':
        // Optional: update UI based on step (questioning, etc)
        break;
    }
  },

  async createProject(name, description) {
    // #region agent log
    debugLogViaTauri('app.js:createProject:entry', 'createProject called', { nameLength: (name || '').length, descriptionLength: (description || '').length }, 'pre-fix', 'H12');
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H12',location:'app.js:createProject:entry',message:'createProject called',data:{nameLength:(name||'').length,descriptionLength:(description||'').length},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    try {
      const res = await fetch(`${this.apiBase}/project/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.replace(/\s+/g, '-').toLowerCase(), description })
      });
      const data = await res.json();
      // #region agent log
      debugLogViaTauri('app.js:createProject:response', 'createProject response received', { success: !!data?.success, projectIdPresent: !!data?.project_id }, 'pre-fix', 'H12');
      fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H12',location:'app.js:createProject:response',message:'createProject response received',data:{success:!!data?.success,projectIdPresent:!!data?.project_id},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      if (data.success) {
        this.currentProject = data.project_id;
        document.getElementById('titlebar-project-name').textContent = name;
        Sidebar.trackProject(data.project_id, name);
        Sidebar.loadRecentProjects();
        return true;
      }
    } catch (err) {
      // #region agent log
      debugLogViaTauri('app.js:createProject:catch', 'createProject request failed', { errorMessage: err?.message || 'unknown' }, 'pre-fix', 'H12');
      fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H12',location:'app.js:createProject:catch',message:'createProject request failed',data:{errorMessage:err?.message||'unknown'},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      console.error('Create project failed:', err);
    }
    return false;
  },

  async sendChatMessage(message) {
    const provider = this.getSavedProvider();
    const apiKey = this.getSavedApiKey();
    // #region agent log
    debugLogViaTauri('app.js:sendChatMessage:entry:tauri', 'sendChatMessage called', { messageLength: (message || '').length, provider, hasApiKey: !!(apiKey && apiKey.trim()) }, 'post-fix', 'H17');
    // #endregion
    // #region agent log
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H3',location:'app.js:sendChatMessage:entry',message:'sendChatMessage called',data:{messageLength:(message||'').length,provider,hasApiKey:!!(apiKey&&apiKey.trim()),currentProject:this.currentProject||null},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    
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
    Activity.thinking();
    
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
        // #region agent log
        fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H3',location:'app.js:sendChatMessage:response',message:'Chat API response received',data:{ok:response.ok,nextAction:data?.next_action||null,hasResponseText:!!data?.response},timestamp:Date.now()})}).catch(()=>{});
        // #endregion
        
        Chat.hideTyping();
        Chat.addAIMessage(data.response);
        Activity.hide();
        
        if (data.next_action === 'start_training') {
            this.startTraining();
        }
        if (data.next_action === 'show_rules') {
            // Refresh file tree and load rule files  
            setTimeout(() => {
                Workspace.refreshFileTree(this.currentProject);
                Workspace.loadRuleFiles(this.currentProject);
            }, 500);
        }
    } catch (e) {
        // #region agent log
        fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H3',location:'app.js:sendChatMessage:catch',message:'Chat API request failed',data:{errorName:e?.name||'unknown',errorMessage:e?.message||'unknown'},timestamp:Date.now()})}).catch(()=>{});
        // #endregion
        Chat.hideTyping();
        Activity.hide();
        Chat.addAIMessage('Engine not reachable. Make sure python scripts/dev.py is running.');
    }
  },

  async startTraining() {
    if (!this.currentProject) return;
    // NOW show the building state
    const waiting = document.getElementById('workspace-waiting');
    const building = document.getElementById('workspace-building-content');
    if (waiting) waiting.style.display = 'none';
    if (building) building.style.display = '';
    Activity.training('Starting training...');
    try {
      await fetch(`${this.apiBase}/train/${this.currentProject}`, { 
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              provider: this.getSavedProvider(),
              api_key: this.getSavedApiKey()
          })
      });
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

function debugLogViaTauri(location, message, data, runId, hypothesisId) {
  if (!window.__TAURI__?.core?.invoke) return;
  const jsonData = JSON.stringify(data || {});
  window.__TAURI__.core.invoke('debug_log_command', {
    location,
    message,
    data: jsonData,
    runId,
    hypothesisId
  }).catch(() => {});
}

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
  // #region agent log
  debugLogViaTauri('app.js:onAppStart:tauri', 'onAppStart entered', { readyState: document.readyState }, 'pre-fix', 'H7');
  // #endregion
  // #region agent log
  window.addEventListener('error', (event) => {
    debugLogViaTauri(
      'app.js:window:error',
      'Unhandled window error captured',
      { message: event.message || 'unknown', source: event.filename || 'unknown', line: event.lineno || null },
      'pre-fix',
      'H8'
    );
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reasonText = typeof event.reason === 'string' ? event.reason : (event.reason?.message || 'unknown');
    debugLogViaTauri(
      'app.js:window:unhandledrejection',
      'Unhandled promise rejection captured',
      { reason: reasonText },
      'pre-fix',
      'H8'
    );
  });
  // #endregion
  // #region agent log
  let __agentClickLogCount = 0;
  let __agentKeyLogCount = 0;
  document.addEventListener('click', (event) => {
    if (__agentClickLogCount >= 6) return;
    __agentClickLogCount += 1;
    const target = event.target;
    const targetId = target?.id || '';
    const targetClass = typeof target?.className === 'string' ? target.className : '';
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H14',location:'app.js:document:click',message:'Document click captured',data:{targetId,targetClass},timestamp:Date.now()})}).catch(()=>{});
  }, true);
  document.addEventListener('keydown', (event) => {
    if (__agentKeyLogCount >= 6) return;
    __agentKeyLogCount += 1;
    const target = event.target;
    const targetId = target?.id || '';
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H14',location:'app.js:document:keydown',message:'Document keydown captured',data:{key:event.key||'',targetId},timestamp:Date.now()})}).catch(()=>{});
  }, true);
  // #endregion
  // #region agent log
  debugLogViaTauri('app.js:onAppStart:methodWiring:tauri', 'Method wiring snapshot', { hasSendMessage: typeof App?.sendMessage === 'function', hasSendChatMessage: typeof App?.sendChatMessage === 'function' }, 'pre-fix', 'H15');
  // #endregion
  // #region agent log
  fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H15',location:'app.js:onAppStart:methodWiring',message:'Method wiring snapshot',data:{hasSendMessage:typeof App?.sendMessage==='function',hasSendChatMessage:typeof App?.sendChatMessage==='function'},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  // #region agent log
  fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H1',location:'app.js:onAppStart:entry',message:'App startup entered',data:{readyState:document.readyState},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  App.init();
  // #region agent log
  fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H1',location:'app.js:onAppStart:postInit',message:'App.init completed',data:{hasWelcomeInput:!!document.getElementById('welcome-input'),hasChatInput:!!document.getElementById('chat-input')},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  
  // Load saved settings
  const savedProvider = App.getSavedProvider();
  const savedKey = App.getSavedApiKey();
  const selector = document.getElementById('settings-model-provider');
  const inputKey = document.getElementById('settings-api-key');
  if (selector) selector.value = savedProvider;
  if (inputKey) inputKey.value = savedKey;
  
  // Start 10s health check interval
  await ModelSelector.checkEngineStatus();
  // #region agent log
  fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H4',location:'app.js:onAppStart:engineHealth',message:'ModelSelector.checkEngineStatus completed',data:{provider:savedProvider,hasApiKey:!!savedKey},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  setInterval(() => ModelSelector.checkEngineStatus(), 10000);
  
  await Sidebar.loadRecentProjects();
  App.connectWebSocket();
  // #region agent log
  fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H5',location:'app.js:onAppStart:websocketInit',message:'WebSocket connection attempted',data:{wsExists:!!App.ws},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  
  const lastProject = localStorage.getItem('dom_last_project');
  if (lastProject) {
      App.currentProject = lastProject;
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', onAppStart);
