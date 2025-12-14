document.addEventListener('DOMContentLoaded', ()=>{
  async function loadMembers(){
    const members = await api('/api/members');
    const root = document.getElementById('membersList');
    if(!root) return;
    root.innerHTML = '';
    members.forEach(m => {
      const el = document.createElement('div');
      el.className = 'list-group-item d-flex justify-content-between align-items-center';
      el.setAttribute('data-mid', m.member_id);
      el.innerHTML = `<div>${m.member_id} <span class="text-muted">| ${m.name}</span></div><div><small class="text-muted">borrowed: ${m.borrowed_books.length}</small> <button class="btn btn-sm btn-outline-primary ms-2 edit-member">Edit</button><button class="btn btn-sm btn-outline-danger ms-1 delete-member">Delete</button></div>`;
      root.appendChild(el);
    });
  }
  loadMembers();

  const addBtn = document.getElementById('addMemberBtn');
  if(addBtn){
    addBtn.addEventListener('click', async ()=>{
      const member_id = document.getElementById('memberId').value.trim();
      const name = document.getElementById('memberName').value.trim();
      const idEl = document.getElementById('memberId');
      const nameEl = document.getElementById('memberName');
      clearFieldError(idEl); clearFieldError(nameEl);
      if(!member_id){ showFieldError(idEl, 'Member ID required'); return; }
      const res = await api('/api/members','POST',{member_id,name});
      if(res.ok){ showToast('Member added','success'); loadMembers(); return; }
      // map field errors if present
      if(res.errors){
        if(res.errors.member_id) showFieldError(idEl, res.errors.member_id);
        if(res.errors.name) showFieldError(nameEl, res.errors.name);
      } else {
        showToast(res.msg||'Failed','danger');
      }
    });
  }

  document.getElementById('membersList').addEventListener('click', async (e)=>{
    const el = e.target.closest('.list-group-item');
    if(!el) return;
    const mid = el.getAttribute('data-mid');
    // delete -> show modal
    if(e.target.classList.contains('delete-member')){
      const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
      document.getElementById('confirmModalBody').textContent = 'Delete this member?';
      const okBtn = document.getElementById('confirmModalOk');
      const onOk = async ()=>{
        const res = await api('/api/members/'+encodeURIComponent(mid),'DELETE');
        if(!res.ok) showToast(res.msg||'Failed','danger');
        else showToast('Your entry is removed','success');
        loadMembers();
        okBtn.removeEventListener('click', onOk);
        confirmModal.hide();
      };
      okBtn.addEventListener('click', onOk);
      confirmModal.show();
      return;
    }

    // edit -> inline inputs
    if(e.target.classList.contains('edit-member')){
      const nameSpan = el.querySelector('.text-muted');
      const currentName = nameSpan ? nameSpan.textContent.replace('| ','') : '';

      // populate member edit modal
      document.getElementById('editMemberName').value = currentName.trim();
      document.getElementById('editMemberId').textContent = mid;
      const editModalEl = document.getElementById('editMemberModal');
      const editModal = new bootstrap.Modal(editModalEl);
      const saveBtn = document.getElementById('editMemberSave');

      const onSave = async ()=>{
        const nameIn = document.getElementById('editMemberName');
        clearFieldError(nameIn);
        const name = nameIn.value.trim();
        if(!name){ showFieldError(nameIn, 'Name is required'); return; }
        const res = await api('/api/members/'+encodeURIComponent(mid),'PUT',{name});
        if(res.ok){
          showToast('Your entry is updated','success');
          editModal.hide();
          saveBtn.removeEventListener('click', onOk);
          loadMembers();
          return;
        }
        // map field errors into modal
        if(res.errors){
          if(res.errors.name) showFieldError(nameIn, res.errors.name);
        } else {
          showToast(res.msg||'Failed','danger');
          editModal.hide();
        }
        // keep modal open when there are field errors
      };
      saveBtn.addEventListener('click', onSave, { once: true });
      editModal.show();
    }
  });
});
