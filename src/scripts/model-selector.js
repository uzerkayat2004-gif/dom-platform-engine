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
        const response = await fetch(`${App.apiBase}/health`);
        const data = await response.json();
        // Show saved provider name if API key exists
        const savedProvider = App.getSavedProvider();
        const savedKey = App.getSavedApiKey();
        const providerLabels = { groq: 'Groq Connected', anthropic: 'Anthropic Connected', openai: 'OpenAI Connected', custom: 'Custom Connected' };
        if (savedKey) {
            this.setModelStatus('connected', providerLabels[savedProvider] || 'Engine Ready');
        } else {
            this.setModelStatus('connected', 'Engine Ready — add API key');
        }
    } catch (e) {
        this.setModelStatus('disconnected', 'Engine Offline');
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
