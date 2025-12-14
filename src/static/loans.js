document.addEventListener('DOMContentLoaded', ()=>{
  const root = document.getElementById('loansList');
  if(!root) return;

  async function loadLoans(){
    const loans = await api('/api/loans');
    root.innerHTML = '';
    loans.forEach(l=>{
      const el = document.createElement('div');
      el.className = 'list-group-item d-flex justify-content-between align-items-start';
      el.innerHTML = `<div><div><strong>Loan ${l.loan_id}</strong></div><div class="text-muted">Member: ${l.member_id} — ISBN: ${l.isbn}</div><div class="text-muted">Due: ${l.due_date} — Issued: ${l.issue_date}</div></div><div class="text-end"><div>${l.returned?'<span class="badge bg-success">Returned</span>':'<span class="badge bg-warning text-dark">Active</span>'}</div><div class="mt-2"><button class="btn btn-sm btn-outline-primary edit-loan" data-loan="${l.loan_id}">Edit</button></div></div>`;
      root.appendChild(el);
    });
  }
  loadLoans();

  root.addEventListener('click', async (e)=>{
    if(!e.target.classList.contains('edit-loan')) return;
    const loanId = e.target.getAttribute('data-loan');
    // get loan details from API list (simple approach)
    const loans = await api('/api/loans');
    const loan = loans.find(x=>x.loan_id===loanId);
    if(!loan) return showToast('Loan not found','danger');

    // populate modal
    document.getElementById('editLoanId').textContent = loan.loan_id;
    document.getElementById('editLoanMember').textContent = loan.member_id;
    document.getElementById('editLoanIsbn').textContent = loan.isbn;
    document.getElementById('editLoanDue').value = loan.due_date;
    document.getElementById('editLoanReturned').checked = !!loan.returned;

    const modalEl = document.getElementById('editLoanModal');
    const modal = new bootstrap.Modal(modalEl);
    const saveBtn = document.getElementById('editLoanSave');
    const onSave = async ()=>{
      const dueIn = document.getElementById('editLoanDue');
      clearFieldError(dueIn);
      const due = dueIn.value;
      if(!due){ showFieldError(dueIn, 'Due date is required'); return; }
      const returned = document.getElementById('editLoanReturned').checked;
      const res = await api('/api/loans/'+encodeURIComponent(loanId),'PUT',{due_date:due, returned});
      if(!res.ok) showToast(res.msg||'Failed','danger'); else showToast('Your entry is updated','success');
      modal.hide();
      saveBtn.removeEventListener('click', onSave);
      loadLoans();
    };
    saveBtn.addEventListener('click', onSave, { once: true });
    modal.show();
  });
});
