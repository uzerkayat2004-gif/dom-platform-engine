/**
 * DOM Platform — Chat Panel
 * chat.js — Messages, typing, input handling, localStorage history
 */

const Chat = {
  messages: [],

  init() {
    this.bindChatInput();
  },

  // ---- localStorage Persistence ----

  _storageKey(projectId) {
    return `dom_chat_${projectId}`;
  },

  saveHistory(projectId) {
    if (!projectId) return;
    try {
      localStorage.setItem(this._storageKey(projectId), JSON.stringify(this.messages));
    } catch (e) {
      console.warn('Chat: could not save history', e);
    }
  },

  loadHistory(projectId) {
    if (!projectId) return [];
    try {
      const raw = localStorage.getItem(this._storageKey(projectId));
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  },

  /**
   * Restore chat history for a project — call when switching to an existing project.
   * Clears the current chat panel and re-renders stored messages.
   */
  restoreHistory(projectId) {
    const history = this.loadHistory(projectId);
    this.clearMessages();

    if (history.length === 0) return;

    history.forEach(msg => {
      if (msg.role === 'user') {
        this._renderUserMessage(msg.content);
      } else if (msg.role === 'assistant') {
        this._renderAIMessage(msg.content);
      }
    });

    this.messages = [...history];
    this.scrollToBottom();
  },

  clearMessages() {
    const container = document.getElementById('chat-messages');
    if (container) {
      // Keep only the typing indicator (last child by class)
      const typing = document.getElementById('typing-indicator');
      container.innerHTML = '';
      if (typing) container.appendChild(typing);
    }
    this.messages = [];
  },

  // ---- Render helpers (internal, no save) ----

  _renderUserMessage(text) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message-user';
    msgDiv.innerHTML = `<div class="message-user-body">${this.escapeHtml(text)}</div>`;
    const typing = document.getElementById('typing-indicator');
    if (typing) container.insertBefore(msgDiv, typing);
    else container.appendChild(msgDiv);
  },

  _renderAIMessage(text) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message-ai';
    msgDiv.innerHTML = `
      <span class="message-ai-label">DOM</span>
      <div class="message-ai-body">${text}</div>
    `;
    const typing = document.getElementById('typing-indicator');
    if (typing) container.insertBefore(msgDiv, typing);
    else container.appendChild(msgDiv);
    return msgDiv;
  },

  // ---- Public message adders (save to localStorage) ----

  bindChatInput() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('btn-chat-send');

    sendBtn.addEventListener('click', () => {
      this.handleSend();
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.handleSend();
      }
    });

    input.addEventListener('input', () => {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    });
  },

  handleSend() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    input.style.height = 'auto';

    App.sendChatMessage(text);
  },

  addUserMessage(text) {
    this._renderUserMessage(text);
    this.messages.push({ role: 'user', content: text });
    this.saveHistory(App.currentProject);
    this.scrollToBottom();
  },

  addAIMessage(text) {
    const msgDiv = this._renderAIMessage(text);

    // Fade in only for new messages (not restored ones)
    if (msgDiv) {
      msgDiv.style.opacity = '0';
      requestAnimationFrame(() => {
        msgDiv.style.transition = 'opacity 300ms ease';
        msgDiv.style.opacity = '1';
      });
    }

    this.messages.push({ role: 'assistant', content: text });
    this.saveHistory(App.currentProject);
    this.scrollToBottom();
  },

  addSystemMessage(text) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message-system';
    msgDiv.innerHTML = `
      <span class="message-system-body">
        ${text}
        <span class="loading-dots"><span></span><span></span><span></span></span>
      </span>
    `;
    container.appendChild(msgDiv);
    this.scrollToBottom();
  },

  showTyping() {
    document.getElementById('typing-indicator').style.display = 'flex';
    this.scrollToBottom();
  },

  hideTyping() {
    document.getElementById('typing-indicator').style.display = 'none';
  },

  scrollToBottom() {
    const container = document.getElementById('chat-messages');
    setTimeout(() => {
      container.scrollTop = container.scrollHeight;
    }, 50);
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
};
