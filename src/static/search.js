document.addEventListener('DOMContentLoaded', ()=>{
  const btn = document.getElementById('searchBtn');
  if(!btn) return;
  btn.addEventListener('click', async ()=>{
    const q = document.getElementById('searchQ').value.trim();
    const t = document.getElementById('searchType').value;
    if(!q) return;
    const res = await api('/api/books');
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
});
