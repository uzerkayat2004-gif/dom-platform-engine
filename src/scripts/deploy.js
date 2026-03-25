/**
 * DOM Platform — Deploy
 * deploy.js — Deploy button logic (placeholder for MVP)
 */

const Deploy = {
  init() {
    this.bindDeployButton();
  },

  bindDeployButton() {
    const deployBtn = document.getElementById('btn-deploy');
    if (deployBtn) {
      deployBtn.addEventListener('click', async () => {
        deployBtn.textContent = 'Deploying...';
        deployBtn.style.opacity = '0.7';
        deployBtn.disabled = true;

        try {
            const response = await fetch(`${App.apiBase}/deploy`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ project_id: App.currentProject || 'new' })
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                deployBtn.textContent = '✓ Deployed';
            } else {
                deployBtn.textContent = 'Failed';
            }
        } catch (e) {
            deployBtn.textContent = 'Error';
        }

        deployBtn.style.opacity = '1';

        setTimeout(() => {
          deployBtn.textContent = 'Deploy App';
          deployBtn.disabled = false;
        }, 3000);
      });
    }
  }
};
