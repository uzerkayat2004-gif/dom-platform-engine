/**
 * DOM Platform — Chat Panel
 * chat.js — Messages, typing, input handling
 */

const Chat = {
  messages: [],

  init() {
    // #region agent log
    if (window.__TAURI__?.core?.invoke) {
      window.__TAURI__.core.invoke('debug_log_command', {
        location: 'chat.js:init:wiring:tauri',
        message: 'Chat init method wiring snapshot',
        data: JSON.stringify({ hasSendMessage: typeof App?.sendMessage === 'function', hasSendChatMessage: typeof App?.sendChatMessage === 'function' }),
        runId: 'pre-fix',
        hypothesisId: 'H15'
      }).catch(() => {});
    }
    // #endregion
    this.bindChatInput();
  },

  bindChatInput() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('btn-chat-send');

    // Send on button click
    sendBtn.addEventListener('click', () => {
      this.handleSend();
    });

    // Send on Enter (Shift+Enter for newline)
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.handleSend();
      }
    });

    // Auto-resize textarea
    input.addEventListener('input', () => {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    });
  },

  handleSend() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    // #region agent log
    if (window.__TAURI__?.core?.invoke) {
      window.__TAURI__.core.invoke('debug_log_command', {
        location: 'chat.js:handleSend:entry:tauri',
        message: 'handleSend invoked from chat UI',
        data: JSON.stringify({ textLength: text.length }),
        runId: 'pre-fix',
        hypothesisId: 'H9'
      }).catch(() => {});
    }
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H9',location:'chat.js:handleSend:entry',message:'handleSend invoked from chat UI',data:{textLength:text.length},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    if (!text) return;
    input.value = '';
    input.style.height = 'auto';

    // Send to backend via App
    // #region agent log
    if (window.__TAURI__?.core?.invoke) {
      window.__TAURI__.core.invoke('debug_log_command', {
        location: 'chat.js:handleSend:tauri',
        message: 'Chat dispatch about to call App method',
        data: JSON.stringify({ textLength: text.length, hasSendMessage: typeof App?.sendMessage === 'function', hasSendChatMessage: typeof App?.sendChatMessage === 'function' }),
        runId: 'pre-fix',
        hypothesisId: 'H2'
      }).catch(() => {});
    }
    fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H2',location:'chat.js:handleSend',message:'Attempting to dispatch chat message via App',data:{textLength:text.length,hasSendMessage:typeof App?.sendMessage==='function',hasSendChatMessage:typeof App?.sendChatMessage==='function'},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    try {
      App.sendChatMessage(text);
    } catch (error) {
      // #region agent log
      if (window.__TAURI__?.core?.invoke) {
        window.__TAURI__.core.invoke('debug_log_command', {
          location: 'chat.js:handleSend:catch:tauri',
          message: 'App.sendMessage threw in chat send',
          data: JSON.stringify({ errorName: error?.name || 'unknown', errorMessage: error?.message || 'unknown' }),
          runId: 'pre-fix',
          hypothesisId: 'H2'
        }).catch(() => {});
      }
      fetch('http://127.0.0.1:7530/ingest/c75c5685-c11a-466d-a1fb-9a520f337f0f',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'48444a'},body:JSON.stringify({sessionId:'48444a',runId:'pre-fix',hypothesisId:'H2',location:'chat.js:handleSend:catch',message:'Dispatch failed while calling App.sendMessage',data:{errorName:error?.name||'unknown',errorMessage:error?.message||'unknown'},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      throw error;
    }
  },

  addUserMessage(text) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message-user';
    msgDiv.innerHTML = `<div class="message-user-body">${this.escapeHtml(text)}</div>`;
    container.appendChild(msgDiv);
    this.scrollToBottom();
    this.messages.push({ role: 'user', content: text });
  },

  addAIMessage(text) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message-ai';
    msgDiv.innerHTML = `
      <span class="message-ai-label">DOM</span>
      <div class="message-ai-body">${text}</div>
    `;
    msgDiv.style.opacity = '0';
    container.appendChild(msgDiv);

    // Fade in
    requestAnimationFrame(() => {
      msgDiv.style.transition = 'opacity 300ms ease';
      msgDiv.style.opacity = '1';
    });

    this.scrollToBottom();
    this.messages.push({ role: 'assistant', content: text });
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

  // Removed simulateAgentResponse as it is now handled by the real backend

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
