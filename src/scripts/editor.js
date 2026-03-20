/**
 * DOM Platform — Editor / Settings
 * editor.js — Rule file editor, suggestion chips, settings interactions
 */

const Editor = {
  init() {
    this.bindSuggestionChips();
    this.bindSettingsInteractions();
  },

  // ---- Suggestion Chips ----
  bindSuggestionChips() {
    const chips = document.querySelectorAll('.suggestion-chip');
    const textarea = document.getElementById('welcome-input');

    const suggestions = {
      'restaurant': 'I want to build a complete restaurant POS system. It should handle orders, menu management, table assignments, payments, and kitchen notifications. Staff login with role-based access — waiters can take orders, managers can approve refunds and discounts.',
      'hospital': 'I want to build a hospital management system. It should handle patient registration, appointment scheduling, doctor assignments, prescription management, and billing. Role-based access for doctors, nurses, receptionists, and administrators.',
      'retail': 'I want to build a retail store management system. It should handle inventory tracking, point of sale, customer loyalty programs, supplier management, and sales reporting. Staff can process sales, managers can adjust pricing and approve returns.',
      'school': 'I want to build a school learning management system. It should handle student enrollment, class scheduling, assignment submissions, grade tracking, and parent communication. Teachers can create content, students can submit work, admins manage everything.'
    };

    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        const key = chip.dataset.suggestion;
        if (suggestions[key]) {
          textarea.value = suggestions[key];
          textarea.focus();

          // Visual feedback
          chips.forEach(c => c.style.borderColor = '');
          chip.style.borderColor = 'var(--border-blue)';
        }
      });
    });
  },

  // ---- Settings Interactions ----
  bindSettingsInteractions() {
    // Slider value display
    this.bindSlider('settings-train-examples', 'val-train-examples');
    this.bindSlider('settings-train-epochs', 'val-train-epochs');

    // Toggle switch
    const toggle = document.getElementById('toggle-compact-mode');
    if (toggle) {
      toggle.addEventListener('click', () => {
        toggle.classList.toggle('active');
      });
    }

    // Test API key button
    const testBtn = document.getElementById('btn-test-key');
    const inputKey = document.getElementById('settings-api-key');
    const selector = document.getElementById('settings-model-provider');
    
    if (testBtn && inputKey && selector) {
      testBtn.addEventListener('click', async () => {
        const provider = selector.value;
        const apiKey = inputKey.value.trim();
        
        testBtn.textContent = '...';
        testBtn.style.opacity = '0.6';

        try {
            const response = await fetch('http://127.0.0.1:8080/api-key/test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({provider, api_key: apiKey})
            });
            const data = await response.json();
            
            if (data.valid) {
              testBtn.textContent = '✓';
              testBtn.style.color = 'var(--success)';
              testBtn.style.borderColor = 'var(--success)';
              testBtn.style.opacity = '1';
            } else {
              testBtn.textContent = 'Failed';
              testBtn.style.color = 'var(--danger)';
              testBtn.style.borderColor = 'var(--danger)';
              testBtn.style.opacity = '1';
            }
        } catch (e) {
            testBtn.textContent = 'Error';
            testBtn.style.color = 'var(--danger)';
            testBtn.style.borderColor = 'var(--danger)';
            testBtn.style.opacity = '1';
        }

        setTimeout(() => {
          testBtn.textContent = 'Test';
          testBtn.style.color = '';
          testBtn.style.borderColor = '';
        }, 3000);
      });
    }

    // Save API key button
    const saveBtn = document.getElementById('btn-save-key');
    if (saveBtn) {
      saveBtn.addEventListener('click', () => {
        if (inputKey && selector) {
          const provider = selector.value;
          const key = inputKey.value.trim();
          App.saveApiKey(provider, key);
        }
        const originalText = saveBtn.textContent;
        saveBtn.textContent = 'Saved ✓';
        setTimeout(() => {
          saveBtn.textContent = originalText;
        }, 1500);
      });
    }
  },

  bindSlider(sliderId, valueId) {
    const slider = document.getElementById(sliderId);
    const valueDisplay = document.getElementById(valueId);

    if (slider && valueDisplay) {
      slider.addEventListener('input', () => {
        valueDisplay.textContent = slider.value;
      });
    }
  }
};
