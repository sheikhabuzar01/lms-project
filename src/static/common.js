async function api(path, method = 'GET', data = null) {
  const opts = { method, headers: {} };
  if (data) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(data);
  }
  const res = await fetch(path, opts);
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res.text();
}

function el(id){ return document.getElementById(id); }

// show toast message; type: 'info'|'success'|'danger'
function showToast(message, type = 'info'){
  const container = document.getElementById('toastContainer');
  if(!container) return alert(message);
  const toastId = 't'+Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>`;
  container.insertAdjacentHTML('beforeend', toastHtml);
  const toastEl = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
  toast.show();
  // remove after hidden
  toastEl.addEventListener('hidden.bs.toast', ()=> toastEl.remove());
}

function showFieldError(inputEl, message){
  if(!inputEl) return;
  inputEl.classList.add('is-invalid');
  const help = inputEl.closest('.mb-2')?.querySelector('.form-text');
  if(help){ help.classList.remove('visually-hidden'); help.textContent = message; }
}

function clearFieldError(inputEl){
  if(!inputEl) return;
  inputEl.classList.remove('is-invalid');
  const help = inputEl.closest('.mb-2')?.querySelector('.form-text');
  if(help){ help.classList.add('visually-hidden'); help.textContent = ''; }
}

// keyboard shortcuts and focus management
document.addEventListener('keydown', (e)=>{
  // ignore when typing in inputs
  const tag = document.activeElement?.tagName?.toLowerCase();
  if(tag === 'input' || tag === 'textarea' || document.activeElement?.isContentEditable) return;

  // press 'n' to focus first quick-add element
  if(e.key === 'n' && !e.ctrlKey && !e.metaKey && !e.altKey){
    const q = document.querySelector('[data-quick="add"]');
    if(q){ q.focus(); e.preventDefault(); }
  }
});

// logout handler: calls server logout endpoint and redirects to homepage
document.addEventListener('DOMContentLoaded', ()=>{
  const logoutBtn = document.getElementById('logoutBtn');
  if(!logoutBtn) return;
  logoutBtn.addEventListener('click', async (e)=>{
    e.preventDefault();
    try{
      const res = await api('/api/logout','POST');
      if(res && res.ok){
        showToast('Logged out','success');
        // redirect to home
        window.location.href = '/';
      } else {
        showToast('Logout failed','danger');
      }
    }catch(err){
      showToast('Logout failed','danger');
    }
  });
});
