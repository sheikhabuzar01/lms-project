document.addEventListener('DOMContentLoaded', ()=>{
  const loginBtn = document.getElementById('loginBtn');
  const registerBtn = document.getElementById('registerBtn');
  const status = document.getElementById('loginStatus');
  if(loginBtn){
    loginBtn.addEventListener('click', async ()=>{
      const u = document.getElementById('user').value.trim();
      const p = document.getElementById('pass').value.trim();
      const res = await api('/api/login','POST',{username:u,password:p});
      status.textContent = res.ok ? 'Logged in' : 'Invalid credentials';
    });
  }
  if(registerBtn){
    registerBtn.addEventListener('click', async ()=>{
      const u = document.getElementById('user').value.trim();
      const p = document.getElementById('pass').value.trim();
      const res = await api('/api/register','POST',{username:u,password:p});
      status.textContent = res.ok ? 'Registered & logged in' : 'Registration failed';
    });
  }
});
