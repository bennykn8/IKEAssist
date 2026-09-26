const $ = (selector) => document.querySelector(selector);
const storageKey = 'ikeassist-conversations-v2';
let chats = [];
try {
  const stored = JSON.parse(localStorage.getItem(storageKey) || 'null');
  // Keep conversations saved by the previous server-session implementation.
  const savedChats = Array.isArray(stored) ? stored : stored?.chats;
  if (Array.isArray(savedChats)) chats = savedChats.filter(c => c && typeof c.id === 'string' && typeof c.title === 'string' && Array.isArray(c.messages));
} catch {}
let activeId = null;
let busy = false;
function save() { try { localStorage.setItem(storageKey, JSON.stringify(chats.slice(0, 30))); } catch {} }
function element(tag, className, text) { const el = document.createElement(tag); el.className = className; if (text !== undefined) el.textContent = text; return el; }
function answerBody(text) {
  const body = element('div', 'message-body');
  for (const line of String(text || '').split('\n')) {
    const row = element('div', /^#{1,4} /.test(line) ? 'answer-heading' : 'answer-line');
    const clean = line.replace(/^#{1,4} /, '').replace(/^[-*] /, '• ');
    for (const part of clean.split(/(\*\*[^*]+\*\*)/g)) row.append(part.startsWith('**') && part.endsWith('**') ? element('strong', '', part.slice(2, -2)) : document.createTextNode(part));
    if (!clean) row.append(document.createElement('br'));
    body.append(row);
  }
  return body;
}
function closeMenu() { $('#sidebar').classList.remove('open'); $('#menu-toggle').setAttribute('aria-expanded', 'false'); }
function renderHistory() {
  const history = $('#history'); history.replaceChildren();
  if (!chats.length) history.append(element('p', '', 'Your next idea starts here.\nConversations appear as you explore.'));
  chats.forEach(chat => { const button = element('button', chat.id === activeId ? 'selected' : '', chat.title); button.title = chat.title; button.onclick = () => { activeId = chat.id; render(); closeMenu(); }; history.append(button); });
}
function render() {
  const chat = chats.find(c => c.id === activeId);
  $('#welcome').hidden = !!chat;
  const conversation = $('#conversation'); conversation.hidden = !chat; conversation.replaceChildren();
  for (const message of chat?.messages || []) {
    const card = element('article', `message ${message.role} ${message.error ? 'error' : ''}`);
    const label = element('div', 'message-label', message.role === 'user' ? 'You' : 'IKEAssist');
    card.append(label, message.pending ? element('div', 'loading', 'Finding thoughtful options for your space…') : answerBody(message.text));
    if (message.error) { const retry = element('button', 'retry', 'Try again'); retry.disabled = busy; retry.onclick = () => submitQuestion(message.question); card.append(retry); }
    if (message.sources?.length) {
      card.append(element('div', 'sources-label', `${message.sources.length} PRODUCT SOURCES`));
      const sources = element('div', 'sources');
      message.sources.forEach((source, i) => {
        let url; try { const parsed = new URL(source.url); if (parsed.protocol === 'https:' && (parsed.hostname === 'ikea.com' || parsed.hostname.endsWith('.ikea.com'))) url = parsed.href; } catch {}
        const tile = element(url ? 'a' : 'div', 'source'); if (url) { tile.href = url; tile.target = '_blank'; tile.rel = 'noopener noreferrer'; }
        tile.append(element('strong', '', `${i + 1}. ${source.name}`), element('p', '', String(source.description || '').slice(0, 180)), element('span', '', [source.price ? `$${source.price} · July 2025` : 'Product catalog', url ? 'View at IKEA' : ''].filter(Boolean).join('   '))); sources.append(tile);
      }); card.append(sources);
    }
    conversation.append(card);
  }
  renderHistory(); $('#send-button').disabled = busy;
  requestAnimationFrame(() => { $('#main-scroll').scrollTop = chat ? $('#main-scroll').scrollHeight : 0; });
}
async function submitQuestion(value) {
  const question = value.trim(); if (!question || busy || question.length > 4000) return;
  let chat = chats.find(c => c.id === activeId);
  if (!chat) { chat = { id: crypto.randomUUID(), title: question, messages: [] }; chats.unshift(chat); activeId = chat.id; }
  chat.messages.push({ role: 'user', text: question });
  const reply = { role: 'assistant', pending: true, text: '' }; chat.messages.push(reply);
  busy = true; $('#question').value = ''; $('#question').style.height = 'auto'; render();
  try {
    const response = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question }), signal: AbortSignal.timeout(240000) });
    const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Something went wrong. Please try again.');
    reply.text = data.answer; reply.sources = data.sources;
  } catch (error) { reply.text = error.name === 'TimeoutError' ? 'This answer took too long. Please check that Ollama is running and try again.' : error.message; reply.error = true; reply.question = question; }
  finally { reply.pending = false; busy = false; save(); render(); }
}
function newChat() { activeId = null; render(); closeMenu(); $('#question').focus(); }
$('#chat-form').addEventListener('submit', event => { event.preventDefault(); submitQuestion($('#question').value); });
$('#question').addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); submitQuestion(event.target.value); } });
$('#question').addEventListener('input', event => { event.target.setCustomValidity(''); event.target.style.height = 'auto'; event.target.style.height = `${Math.min(event.target.scrollHeight, 130)}px`; });
document.querySelectorAll('[data-question]').forEach(button => button.onclick = () => { $('#question').value = button.dataset.question; $('#question').focus(); });
$('#new-chat').onclick = newChat;
$('#assistant-nav').onclick = () => { closeMenu(); $('#question').focus(); };
$('#about-button').onclick = $('#details-button').onclick = () => $('#about-dialog').showModal();
$('#close-dialog').onclick = () => $('#about-dialog').close();
$('#menu-toggle').onclick = () => { const open = $('#sidebar').classList.toggle('open'); $('#menu-toggle').setAttribute('aria-expanded', String(open)); };
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); if (event.key.toLowerCase() === 'n' && !event.ctrlKey && !event.metaKey && !event.altKey && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) && !$('#about-dialog').open) newChat(); });
document.querySelector('main').addEventListener('click', event => { if (!event.target.closest('#menu-toggle')) closeMenu(); });
render();
