(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const content = $('#book-content');
  const blocks = [...content.querySelectorAll(':scope > .book-section')];
  const chapterBlocks = blocks.filter(e => e.dataset.chapter);
  const reader = chapterBlocks.length > 0;
  const navLinks = [...$('#book-nav').querySelectorAll('a')];
  const toc = $('#toc-nav');
  const mode = $('#reading-mode');
  const sourceToggle = $('#source-toggle');
  const dialog = $('#search-dialog');
  const searchInput = $('#search-input');
  let full = false;
  let current = blocks[0] || content;
  let tocHeadings = [];
  let lastOpener = null;
  let scrollQueued = false;
  const escapeHTML = value => value.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const plainHeading = element => element?.dataset.title || element?.textContent.replace(/¶$/, '').trim() || '';
  const headingOf = block => plainHeading(block.querySelector('h1'));
  const shortTitle = block => headingOf(block).split('｜').pop();
  function fragment() { try { return decodeURIComponent(location.hash.slice(1)); } catch { return location.hash.slice(1); } }
  function closeDrawer() {
    $('#book-sidebar').classList.remove('open');
    $('#drawer-backdrop').hidden = true;
    $('#menu-button').setAttribute('aria-expanded', 'false');
  }
  function closeToc() { $('#page-toc').classList.remove('open'); $('#toc-button').setAttribute('aria-expanded', 'false'); }
  function setCurrent(block) {
    current = block;
    for (const a of navLinks) {
      const active = reader ? (a.getAttribute('href') === '#' + block.id || (!block.dataset.chapter && block.id === 'book-home' && a.getAttribute('href') === '#book-home')) : a.pathname === location.pathname;
      a.classList.toggle('active', active);
      if (active) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    }
    $('#reading-context').textContent = block.dataset.chapter ? '第 ' + Number(block.dataset.chapter) + ' 章' : reader ? '全书导读' : '随用随查';
    $('#header-context').textContent = reader ? shortTitle(block) : document.title;
    document.title = reader && block.dataset.chapter ? shortTitle(block) + ' · DeepSeek Harness' : document.documentElement.dataset.pageTitle;
    updateToc();
    updateTurns();
  }
  function updateToc() {
    tocHeadings = [...current.querySelectorAll('h2[id],h3[id]')].filter(h => !(sourceToggle.checked && h.closest('.source-section')));
    toc.replaceChildren();
    for (const h of tocHeadings) {
      const a = document.createElement('a');
      a.href = '#' + h.id; a.textContent = plainHeading(h);
      if (h.tagName === 'H3') a.className = 'subheading';
      toc.append(a);
    }
    markToc();
  }
  function markToc() {
    let active = tocHeadings[0];
    for (const h of tocHeadings) if (h.getBoundingClientRect().top <= 150) active = h;
    for (const a of toc.children) {
      const on = a.hash === '#' + active?.id;
      a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
    }
  }
  function updateTurns() {
    const turns = $('#page-turns');
    if (!reader) return;
    turns.hidden = false;
    const index = blocks.indexOf(current);
    turns.replaceChildren();
    for (const [next, label] of [[blocks[index - 1], '← 上一章'], [blocks[index + 1], '下一章 →']]) {
      if (!next) { turns.append(document.createElement('span')); continue; }
      const a = document.createElement('a'); a.href = '#' + next.id;
      const small = document.createElement('small'); small.textContent = label;
      const title = document.createElement('span'); title.textContent = next.dataset.chapter ? '第 ' + Number(next.dataset.chapter) + ' 章 · ' + shortTitle(next) : '全书导读';
      a.append(small, title); turns.append(a);
    }
  }
  function showTarget(scroll = true) {
    const id = fragment();
    const target = id ? document.getElementById(id) : null;
    const block = target?.closest('.book-section') || (id === 'content' || id === 'top' ? current : blocks[0]) || content;
    if (reader) for (const b of blocks) b.hidden = !full && b !== block;
    if (target?.closest('.source-section') && sourceToggle.checked) {
      sourceToggle.checked = false; document.body.classList.remove('hide-source');
    }
    setCurrent(block);
    closeDrawer(); closeToc();
    if (scroll) requestAnimationFrame(() => {
      if (target && id !== 'top') target.scrollIntoView({block:'start', behavior:'instant'});
      else window.scrollTo({top:0, behavior:'instant'});
    });
  }
  document.documentElement.dataset.pageTitle = document.title;
  for (const h of content.querySelectorAll('h1[id],h2[id],h3[id]')) {
    h.dataset.title = h.textContent;
    const a = document.createElement('a'); a.className = 'heading-link'; a.href = '#' + h.id; a.textContent = '¶'; a.setAttribute('aria-label', '链接到：' + h.textContent); h.append(a);
  }
  sourceToggle.addEventListener('change', () => { document.body.classList.toggle('hide-source', sourceToggle.checked); updateToc(); });
  if (reader) {
    mode.hidden = false;
    mode.addEventListener('click', () => {
      const anchor = current;
      full = !full;
      mode.textContent = full ? '按章阅读' : '全文阅读';
      mode.setAttribute('aria-pressed', String(full));
      for (const b of blocks) b.hidden = !full && b !== anchor;
      updateToc();
      requestAnimationFrame(() => anchor.scrollIntoView({block:'start',behavior:'instant'}));
    });
  }
  window.addEventListener('hashchange', () => showTarget());
  window.addEventListener('scroll', () => {
    if (scrollQueued) return;
    scrollQueued = true;
    requestAnimationFrame(() => {
      if (reader && full) {
        let active = blocks[0];
        for (const b of blocks) if (b.getBoundingClientRect().top <= 160) active = b;
        if (active !== current) setCurrent(active);
      }
      markToc(); scrollQueued = false;
    });
  }, {passive:true});
  $('#book-nav').addEventListener('click', e => { if (e.target.closest('a')) closeDrawer(); });
  toc.addEventListener('click', e => { if (e.target.closest('a')) closeToc(); });
  $('#menu-button').addEventListener('click', () => {
    const open = $('#book-sidebar').classList.toggle('open');
    $('#menu-button').setAttribute('aria-expanded', String(open));
    $('#drawer-backdrop').hidden = !open;
    if (open) (navLinks.find(a => a.classList.contains('active')) || navLinks[0])?.focus();
  });
  $('#drawer-backdrop').addEventListener('click', closeDrawer);
  $('#toc-button').addEventListener('click', () => {
    const open = $('#page-toc').classList.toggle('open'); $('#toc-button').setAttribute('aria-expanded', String(open));
  });
  $('#back-top').addEventListener('click', e => { e.preventDefault(); window.scrollTo({top:0,behavior:'instant'}); });
  const searchRows = [];
  for (const block of (reader ? blocks : [content])) {
    let heading = block.querySelector('h1')?.id;
    for (const node of block.querySelectorAll('h1,h2,h3,p,li,td')) {
      if (node.matches('h1,h2,h3')) heading = node.id;
      if (node.closest('.chapter-overview') || node.closest('table') && node.cellIndex === undefined) continue;
      const text = node.textContent.replace(/¶$/, '').trim();
      if (text.length < 2) continue;
      searchRows.push({text, lower:text.toLocaleLowerCase(), target:heading || block.id, title:heading ? plainHeading(document.getElementById(heading)) : headingOf(block), chapter:reader ? shortTitle(block) : document.title, section:node.closest('.source-section') !== null, heading:node.matches('h1,h2,h3')});
    }
  }
  function highlight(text, terms) {
    const longest = [...terms].sort((a,b) => b.length-a.length);
    const pattern = new RegExp(longest.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'giu');
    let last = 0, result = '';
    for (const hit of text.matchAll(pattern)) { result += escapeHTML(text.slice(last, hit.index)) + '<mark>' + escapeHTML(hit[0]) + '</mark>'; last = hit.index + hit[0].length; }
    return result + escapeHTML(text.slice(last));
  }
  function search() {
    const value = searchInput.value.trim();
    const results = $('#search-results'); results.replaceChildren();
    if (!value) { $('#search-status').textContent = '搜索当前阅读文件的正文和标题'; return; }
    const terms = value.toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const seen = new Set();
    const rows = searchRows.filter(r => terms.every(t => r.lower.includes(t))).sort((a,b) => Number(b.heading)-Number(a.heading)).filter(r => {const key=r.target+'|'+r.text;if(seen.has(key))return false;seen.add(key);return true;});
    $('#search-status').textContent = rows.length ? '找到 ' + rows.length + ' 处匹配' + (rows.length > 60 ? '，显示前 60 处' : '') : '没有找到匹配内容，试试工具名称或更短的关键词。';
    for (const r of rows.slice(0,60)) {
      const at = Math.max(0, r.lower.indexOf(terms[0])-35);
      const snippet = (at ? '…' : '') + r.text.slice(at,at+160) + (r.text.length>at+160 ? '…' : '');
      const a = document.createElement('a'); a.href = '#' + r.target;
      a.innerHTML = '<small>' + escapeHTML(r.chapter) + (r.section ? ' · 源码研读' : '') + '</small><strong>' + highlight(r.title,terms) + '</strong><p>' + highlight(snippet,terms) + '</p>';
      a.addEventListener('click', () => { dialog.close(); if(location.hash === a.hash) showTarget(); });
      results.append(a);
    }
  }
  function openSearch() { lastOpener = document.activeElement; closeDrawer(); closeToc(); dialog.showModal(); searchInput.focus(); }
  $('#search-button').addEventListener('click', openSearch);
  $('#search-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => lastOpener?.focus());
  dialog.addEventListener('click', e => { const r=dialog.getBoundingClientRect(); if(e.target===dialog&&(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom))dialog.close(); });
  searchInput.addEventListener('input', search);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { closeDrawer(); closeToc(); }
    if (e.key === '/' && !dialog.open && !e.ctrlKey && !e.metaKey && !e.altKey && !e.target.closest('input,textarea,[contenteditable]')) { e.preventDefault(); openSearch(); }
  });
  showTarget();
})();
