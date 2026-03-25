/**
 * DOM Platform — Deploy
 * deploy.js — Deploy button logic for preparing projects for distribution
 */

const Deploy = {
  init() {
    this.bindDeployButton();
  },

bindDeployButton() {
    const deployBtn = document.getElementById('btn-deploy');
    if (deployBtn) {
      deployBtn.addEventListener('click', async () => {
        deployBtn.textContent = 'Checking...';
        deployBtn.style.opacity = '0.7';
        deployBtn.disabled = true;

        try {
          const response = await fetch(`${App.apiBase}/deploy`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ project_id: App.currentProject })
          });
          const data = await response.json();

          if (data.status === 'success') {
            if (data.message === 'Project ready for deployment') {
              deployBtn.textContent = '✓ Ready';
              showNotification('Project is ready for deployment! Check console for deployment details.', 'success');
              console.log('Deployment info:', data.deployment_info);
            } else {
              deployBtn.textContent = '✓ Deployed';
              showNotification('Deployment successful!', 'success');
            }
          } else {
            deployBtn.textContent = '✗ Failed';
            showNotification(`Deployment failed: ${data.message || 'Unknown error'}`, 'error');
          }
        } catch (e) {
          deployBtn.textContent = '✗ Error';
          showNotification('Deployment error. Is the engine running?', 'error');
          console.error('Deployment error:', e);
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
