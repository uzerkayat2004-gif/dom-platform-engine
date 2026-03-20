/**
 * DOM Platform — Model Selector
 * model-selector.js — API key management, model provider switching
 */

const ModelSelector = {
  currentProvider: 'groq',

  init() {
    this.bindProviderSelector();
  },

  bindProviderSelector() {
    const selector = document.getElementById('settings-model-provider');
    if (selector) {
      selector.addEventListener('change', () => {
        this.currentProvider = selector.value;
        App.config.provider = selector.value;

        // Update sidebar model status text
        const statusText = document.querySelector('.model-status-text');
        const statusDot = document.querySelector('.model-status-dot');

        const providerNames = {
          'groq': 'Groq Connected',
          'anthropic': 'Anthropic Connected',
          'openai': 'OpenAI Connected',
          'custom': 'Custom Model'
        };

        if (statusText) {
          statusText.textContent = providerNames[this.currentProvider] || 'Connected';
        }
      });
    }
  },
  
  async checkEngineStatus() {
    try {
        const response = await fetch('http://127.0.0.1:8080/health');
        const data = await response.json();
        this.setModelStatus('connected', data.provider || 'Engine Ready');
    } catch (e) {
        this.setModelStatus('disconnected', 'Engine not running');
    }
  },
  
  setModelStatus(state, text) {
    const statusText = document.querySelector('.model-status-text');
    const statusDot = document.querySelector('.model-status-dot');
    
    if (statusText) statusText.textContent = text;
    
    if (statusDot) {
      if (state === 'connected') {
        statusDot.style.background = 'var(--success)';
        statusDot.style.boxShadow = '0 0 8px var(--success)';
      } else {
        statusDot.style.background = 'var(--danger)';
        statusDot.style.boxShadow = '0 0 8px var(--danger)';
      }
    }
  }
};
