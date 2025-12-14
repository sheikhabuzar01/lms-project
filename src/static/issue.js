document.addEventListener('DOMContentLoaded', ()=>{
  const issueBtn = document.getElementById('issueBtn');
  const returnBtn = document.getElementById('returnBtn');
  const msgEl = document.getElementById('issueMsg');

  async function refresh(){ /* nothing else to load */ }
  refresh();

  if(issueBtn){
    issueBtn.addEventListener('click', async ()=>{
      const member_id = document.getElementById('issueMember').value.trim();
      const isbn = document.getElementById('issueIsbn').value.trim();
      const res = await api('/api/issue','POST',{member_id,isbn});
      msgEl.textContent = res.msg || JSON.stringify(res);
    });
  }
  if(returnBtn){
    returnBtn.addEventListener('click', async ()=>{
      const member_id = document.getElementById('issueMember').value.trim();
      const isbn = document.getElementById('issueIsbn').value.trim();
      const res = await api('/api/return','POST',{member_id,isbn});
      msgEl.textContent = res.msg || JSON.stringify(res);
    });
  }
});
