document.addEventListener('DOMContentLoaded', ()=>{
  async function loadBooks(){
    const books = await api('/api/books');
    const root = document.getElementById('booksList');
    root.innerHTML = '';
    books.forEach(b => {
      const el = document.createElement('div');
      el.className = 'list-group-item d-flex justify-content-between align-items-start';
      el.setAttribute('data-isbn', b.isbn);
      el.innerHTML = `<div><div class="book-title">${b.title}</div><div class="text-muted">${b.author}</div><small class="text-muted">ISBN: ${b.isbn}</small></div><div class="text-end"><div>copies: <strong>${b.copies}</strong></div><div class="mt-2"><button class="btn btn-sm btn-outline-primary me-1 edit-book">Edit</button><button class="btn btn-sm btn-outline-danger delete-book">Delete</button></div></div>`;
      root.appendChild(el);
    });
  }
  loadBooks();

  const addBtn = document.getElementById('addBookBtn');
  if(addBtn){
    addBtn.addEventListener('click', async ()=>{
      const isbnIn = document.getElementById('bookIsbn');
      const titleIn = document.getElementById('bookTitle');
      const authorIn = document.getElementById('bookAuthor');
      const copiesIn = document.getElementById('bookCopies');
      const isbn = isbnIn.value.trim();
      const title = titleIn.value.trim();
      const author = authorIn.value.trim();
      const copies = parseInt(copiesIn.value || '0', 10);
      if(!isbn) { showFieldError(isbnIn, 'ISBN required'); return; }
      // clear previous
      clearFieldError(isbnIn); clearFieldError(titleIn); clearFieldError(copiesIn);
      const res = await api('/api/books','POST',{isbn,title,author,copies});
      if(!res.ok){
        if(res.errors){ if(res.errors.isbn) showFieldError(isbnIn, res.errors.isbn); if(res.errors.title) showFieldError(titleIn, res.errors.title); if(res.errors.copies) showFieldError(copiesIn, res.errors.copies); }
        showToast(res.msg||'Failed','danger');
      }
      loadBooks();
    });
  }

  // delegate edit/delete with inline edit and confirmation modal
  document.getElementById('booksList').addEventListener('click', async (e)=>{
    const el = e.target.closest('.list-group-item');
    if(!el) return;
    const isbn = el.getAttribute('data-isbn');
    // delete flow: show confirm modal
    if(e.target.classList.contains('delete-book')){
      const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
      document.getElementById('confirmModalBody').textContent = 'Delete this book?';
      const okBtn = document.getElementById('confirmModalOk');
      const onOk = async ()=>{
        const res = await api('/api/books/'+encodeURIComponent(isbn),'DELETE');
        if(!res.ok) showToast(res.msg||'Failed','danger');
        else showToast('Your entry is removed','success');
        loadBooks();
        okBtn.removeEventListener('click', onOk);
        confirmModal.hide();
      };
      okBtn.addEventListener('click', onOk);
      confirmModal.show();
      return;
    }

    // edit flow: open edit modal
    if(e.target.classList.contains('edit-book')){
      const titleEl = el.querySelector('.book-title');
      const authorEl = el.querySelector('.text-muted');
      const copiesEl = el.querySelector('strong');
      const currentTitle = titleEl.textContent;
      const currentAuthor = authorEl.textContent;
      const currentCopies = copiesEl.textContent;

      // populate modal fields
      document.getElementById('editBookTitle').value = currentTitle;
      document.getElementById('editBookAuthor').value = currentAuthor;
      document.getElementById('editBookCopies').value = currentCopies;
      document.getElementById('editBookIsbn').textContent = isbn;

      const editModalEl = document.getElementById('editBookModal');
      const editModal = new bootstrap.Modal(editModalEl);
      const saveBtn = document.getElementById('editBookSave');

      const onSave = async ()=>{
        // validation
        const titleIn = document.getElementById('editBookTitle');
        const authorIn = document.getElementById('editBookAuthor');
        const copiesIn = document.getElementById('editBookCopies');
        clearFieldError(titleIn); clearFieldError(authorIn); clearFieldError(copiesIn);
        let ok = true;
        if(!titleIn.value.trim()){ showFieldError(titleIn, 'Title is required'); ok = false; }
        if(!authorIn.value.trim()){ showFieldError(authorIn, 'Author is required'); ok = false; }
        const copiesVal = Number(copiesIn.value);
        if(Number.isNaN(copiesVal) || copiesVal < 0){ showFieldError(copiesIn, 'Enter a non-negative number'); ok = false; }
        if(!ok) return;
        const title = titleIn.value.trim();
        const author = authorIn.value.trim();
        const copies = copiesVal;
        const res = await api('/api/books/'+encodeURIComponent(isbn),'PUT',{title,author,copies});
        if(!res.ok){
          if(res.errors){ if(res.errors.title) showFieldError(document.getElementById('editBookTitle'), res.errors.title); if(res.errors.author) showFieldError(document.getElementById('editBookAuthor'), res.errors.author); if(res.errors.copies) showFieldError(document.getElementById('editBookCopies'), res.errors.copies); }
          showToast(res.msg||'Failed','danger');
        } else showToast('Your entry is updated','success');
        editModal.hide();
        saveBtn.removeEventListener('click', onSave);
        loadBooks();
      };

      saveBtn.addEventListener('click', onSave, { once: true });
      editModal.show();
    }
  });
});
