const loginForm = document.querySelector('[data-login-form]');
if (loginForm) {
  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = loginForm.querySelector('button');
    const message = loginForm.querySelector('[data-form-message]');
    button.disabled = true;
    message.textContent = '正在登录…';
    try {
      const payload = Object.fromEntries(new FormData(loginForm).entries());
      const response = await fetch('/auth/api/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || '登录失败');
      window.location.href = result.redirect || '/dashboard';
    } catch (error) {
      message.textContent = error.message;
      button.disabled = false;
    }
  });
}

const logoutButton = document.querySelector('[data-logout]');
if (logoutButton) {
  logoutButton.addEventListener('click', async () => {
    logoutButton.disabled = true;
    const token = document.querySelector('#csrf-token')?.value || '';
    const response = await fetch('/auth/api/logout', {method: 'POST', headers: {'X-CSRF-Token': token}});
    const result = await response.json();
    window.location.href = result.redirect || '/auth/login';
  });
}
