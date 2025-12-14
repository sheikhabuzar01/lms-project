async function api(path, method = 'GET', data = null) {
  const opts = { method, headers: {} };
  if (data) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(data);
  }
  const res = await fetch(path, opts);
  return res.json();
}

async function loadBooks(){
  const books = await api('/api/books');
  const root = document.getElementById('booksList');
  root.innerHTML = '';
  books.forEach(b => {
    const el = document.createElement('div');
    el.className = 'list-group-item';
    el.innerHTML = `<div class="d-flex justify-content-between"><div><div class="book-title">${b.title}</div><div class="text-muted">${b.author}</div></div><div>ISBN:${b.isbn}<br>copies:${b.copies}</div></div>`;
    root.appendChild(el);
  });
}

async function loadMembers(){
  const members = await api('/api/members');
  const root = document.getElementById('membersList');
  root.innerHTML = '';
  members.forEach(m => {
    const el = document.createElement('div');
    el.className = 'list-group-item';
    el.textContent = `${m.member_id} | ${m.name} | borrowed:${m.borrowed_books.length}`;
    root.appendChild(el);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadBooks();
  loadMembers();

  document.getElementById('addBookBtn').addEventListener('click', async ()=>{
    const isbn = document.getElementById('bookIsbn').value.trim();
    const title = document.getElementById('bookTitle').value.trim();
    const author = document.getElementById('bookAuthor').value.trim();
    const copies = document.getElementById('bookCopies').value || 0;
    if(!isbn) return alert('ISBN required');
    await api('/api/books','POST',{isbn,title,author,copies});
    loadBooks();
  });

  document.getElementById('addMemberBtn').addEventListener('click', async ()=>{
    const member_id = document.getElementById('memberId').value.trim();
    const name = document.getElementById('memberName').value.trim();
    if(!member_id) return alert('Member ID required');
    await api('/api/members','POST',{member_id,name});
    loadMembers();
  });

  document.getElementById('issueBtn').addEventListener('click', async ()=>{
    const member_id = document.getElementById('issueMember').value.trim();
    const isbn = document.getElementById('issueIsbn').value.trim();
    const res = await api('/api/issue','POST',{member_id,isbn});
    document.getElementById('issueMsg').textContent = res.msg || JSON.stringify(res);
    loadBooks(); loadMembers();
  });

  document.getElementById('returnBtn').addEventListener('click', async ()=>{
    const member_id = document.getElementById('issueMember').value.trim();
    const isbn = document.getElementById('issueIsbn').value.trim();
    const res = await api('/api/return','POST',{member_id,isbn});
    document.getElementById('issueMsg').textContent = res.msg || JSON.stringify(res);
    loadBooks(); loadMembers();
  });

  document.getElementById('searchBtn').addEventListener('click', async ()=>{
    const q = document.getElementById('searchQ').value.trim();
    const t = document.getElementById('searchType').value;
    if(!q) return;
    let res;
    if(t==='title') res = await api('/api/books');
    else if(t==='author') res = await api('/api/books');
    else res = await api('/api/books');
    // client-side filter for simplicity
    const results = res.filter(b => {
      if(t==='title') return b.title.toLowerCase().includes(q.toLowerCase());
      if(t==='author') return b.author.toLowerCase().includes(q.toLowerCase());
      return b.isbn===q;
    });
    const root = document.getElementById('searchResults'); root.innerHTML='';
    results.forEach(b=>{
      const el = document.createElement('div'); el.className='list-group-item'; el.textContent = `${b.title} | ${b.author} | ISBN:${b.isbn} | copies:${b.copies}`; root.appendChild(el);
    });
  });

  document.getElementById('loginBtn').addEventListener('click', async ()=>{
    const u = document.getElementById('user').value.trim();
    const p = document.getElementById('pass').value.trim();
    const res = await api('/api/login','POST',{username:u,password:p});
    document.getElementById('loginStatus').textContent = res.ok ? 'Logged in' : 'Invalid';
  });

  document.getElementById('registerBtn').addEventListener('click', async ()=>{
    const u = document.getElementById('user').value.trim();
    const p = document.getElementById('pass').value.trim();
    const res = await api('/api/save','POST');
    alert('Registration from UI not implemented; use CLI or GUI for admin registration');
  });

  document.getElementById('saveBtn').addEventListener('click', async ()=>{
    await api('/api/save','POST'); alert('Saved');
  });
});
