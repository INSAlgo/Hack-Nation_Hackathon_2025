let sessionId = null;
const chatEl = document.getElementById('chat');
const statusEl = document.getElementById('status');

function appendMessage(role, content){
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  div.innerHTML = `<span class="role">${role}:</span><span class="content"></span>`;
  div.querySelector('.content').textContent = content;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function sendPrompt(prompt, model){
  statusEl.textContent = 'Sending...';
  try {
    const body = { prompt };
    if (sessionId) body.session_id = sessionId;
    if (model) body.model = model;
    const r = await fetch('/chat', {
      method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)
    });
    const data = await r.json();
    if (!r.ok){ throw new Error(data.error || 'Request failed'); }
    sessionId = data.session_id;
    appendMessage('assistant', data.reply);
    statusEl.textContent = 'OK';
  } catch(e){
    statusEl.textContent = 'Error';
    appendMessage('system', 'Error: ' + e.message);
  }
}

document.getElementById('prompt-form').addEventListener('submit', e => {
  e.preventDefault();
  const prompt = document.getElementById('prompt').value.trim();
  const model = document.getElementById('model').value.trim();
  if(!prompt) return;
  appendMessage('user', prompt);
  document.getElementById('prompt').value='';
  sendPrompt(prompt, model || null);
});
