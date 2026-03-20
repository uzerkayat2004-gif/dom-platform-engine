/**
 * DOM Platform — Chat Panel
 * chat.js — Messages, typing, input handling
 */

const Chat = {
  messages: [],

  init() {
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
    if (!text) return;

    // Don't add user message here — sendChatMessage does it
    input.value = '';
    input.style.height = 'auto';

    // Send to backend via App
    App.sendChatMessage(text);
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
