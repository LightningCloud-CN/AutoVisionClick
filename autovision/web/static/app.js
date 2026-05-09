/* ═══════════════ AutoVision Frontend ═══════════════ */

// ── State ──
const S = {
  socket: null,
  project: null,      // project state from /api/project/state
  scripts: [],        // [{name, enabled, ...}]
  templates: [],      // ["a.png", ...]
  currentScript: null,
  currentScriptData: null,
  selectedNodePath: null,
  modules: [],
  running: false,
  logCount: 0,
};

// ── DOM refs ──
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

// ── API ──
const API = {
  async _fetch(method, url, body) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const r = await fetch(url, opts);
    return r.json();
  },
  get(url) { return this._fetch('GET', url); },
  post(url, body) { return this._fetch('POST', url, body); },
  put(url, body) { return this._fetch('PUT', url, body); },
  del(url, body) { return this._fetch('DELETE', url, body); },

  projectNew(name, directory) { return this.post('/api/project/new', { name, directory }); },
  projectOpen(directory) { return this.post('/api/project/open', { directory }); },
  projectSave() { return this.post('/api/project/save'); },
  projectState() { return this.get('/api/project/state'); },

  runtimeStart() { return this.post('/api/runtime/start'); },
  runtimeStop() { return this.post('/api/runtime/stop'); },
  runtimePause() { return this.post('/api/runtime/pause'); },
  runtimeEmergency() { return this.post('/api/runtime/emergency'); },

  listScripts() { return this.get('/api/scripts'); },
  createScript(name) { return this.post('/api/script/create', { name }); },
  deleteScript(name) { return this.del(`/api/script/${encodeURIComponent(name)}`); },
  getScript(name) { return this.get(`/api/script/${encodeURIComponent(name)}`); },
  updateScript(name, data) { return this.put(`/api/script/${encodeURIComponent(name)}`, data); },
  addNode(name, parentPath, subtype) {
    return this.post(`/api/script/${encodeURIComponent(name)}/node`, { parent_path: parentPath, subtype });
  },
  deleteNode(name, nodePath) {
    return this.del(`/api/script/${encodeURIComponent(name)}/node`, { node_path: nodePath });
  },
  moveNode(name, nodePath, direction) {
    return this.put(`/api/script/${encodeURIComponent(name)}/node/move`, { node_path: nodePath, direction });
  },
  updateNodeConfig(name, nodePath, key, value) {
    return this.put(`/api/script/${encodeURIComponent(name)}/node/config`, { node_path: nodePath, key, value });
  },

  listTemplates() { return this.get('/api/templates'); },
  deleteTemplate(name) { return this.del(`/api/templates/${encodeURIComponent(name)}`); },
  listWindows() { return this.get('/api/tools/list_windows'); },
  getModules() { return this.get('/api/modules'); },
  wizardGenerate(data) { return this.post('/api/wizard/generate', data); },

  captureTemplate() {
    const sid = S.socket?.id;
    return this.post(`/api/tools/capture_template?sid=${sid}`);
  },
  pickCoordinate() {
    const sid = S.socket?.id;
    return this.post(`/api/tools/pick_coordinate?sid=${sid}`);
  },
};

// ── Toast ──
function toast(msg, type = 'info') {
  const c = $('#toast-container');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  c.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity 0.3s'; }, 2500);
  setTimeout(() => el.remove(), 2800);
}

// ── Status bar ──
function setStatus(state) {
  const el = $('#toolbar-status');
  el.className = 'toolbar-status ' + state;
  el.textContent = { running: '● 运行中', paused: '● 已暂停', stopped: '● 已停止', idle: '● 空闲' }[state] || '● 空闲';
}

// ═══════════════ SCRIPT LIST ═══════════════
function renderScriptList() {
  const el = $('#script-list');
  if (!S.scripts.length) { el.innerHTML = '<div class="empty-hint">暂无脚本，点击 + 创建</div>'; return; }
  el.innerHTML = S.scripts.map(s => {
    const cls = (S.currentScript === s.name) ? 'script-item active' : 'script-item';
    const dot = s.enabled !== false ? 'on' : 'off';
    return `<div class="${cls}" data-name="${s.name}" onclick="selectScript('${esc(s.name)}')">
      <span class="script-enabled-dot ${dot}"></span>
      <span class="script-name">${esc(s.name)}</span>
    </div>`;
  }).join('');
}

function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

async function selectScript(name) {
  S.currentScript = name;
  const r = await API.getScript(name);
  if (r.success) {
    S.currentScriptData = r.script;
    S.selectedNodePath = null;
    renderScriptList();
    renderScriptMeta();
    renderTree();
    renderProperties(null);
    renderMiniFlow(null);
  }
}

// ── Script meta bar ──
function renderScriptMeta() {
  const d = S.currentScriptData;
  if (!d) { $('#script-meta').style.display = 'none'; $('#current-script-name').textContent = '选择一个脚本'; return; }
  $('#script-meta').style.display = 'flex';
  $('#current-script-name').textContent = d.name;
  $('#script-enabled').checked = d.enabled !== false;
  $('#script-tick').value = d.tick_ms || 500;
  $('#script-window').value = d.window_title || '';
}

['#script-enabled', '#script-tick', '#script-window'].forEach(sel => {
  $(sel).addEventListener('change', async () => {
    if (!S.currentScript) return;
    const data = {
      enabled: $('#script-enabled').checked,
      tick_ms: parseInt($('#script-tick').value) || 500,
      window_title: $('#script-window').value,
    };
    await API.updateScript(S.currentScript, data);
    refreshAll();
  });
});

// ═══════════════ MODULE PALETTE ═══════════════
function renderModulePalette() {
  const el = $('#module-palette');
  const cats = ['trigger','action','condition','loop','group'];
  const names = { trigger:'触发器', action:'动作', condition:'条件', loop:'循环', group:'分组' };
  const colors = {
    trigger: 'var(--red)', action: 'var(--green)', condition: 'var(--yellow)',
    loop: 'var(--blue)', group: 'var(--text2)'
  };
  el.innerHTML = cats.map(cat => {
    const mods = S.modules.filter(m => m.category === cat);
    if (!mods.length) return '';
    return `<div class="accordion">
      <div class="accordion-header" data-cat="${cat}" onclick="toggleAccordion(this)" style="color:${colors[cat]}">
        <span class="arrow">▶</span> ${names[cat]}
      </div>
      <div class="accordion-body" data-cat-body="${cat}">
        ${mods.map(m => `
          <div class="module-btn" onclick="addModule('${m.subtype}')">
            <span>${m.icon}</span> <span>${m.label}</span>
          </div>`).join('')}
      </div></div>`;
  }).join('');

  // Open first accordion
  const first = el.querySelector('.accordion-header');
  if (first) toggleAccordion(first, true);
}

function toggleAccordion(hdr, force) {
  const open = force !== undefined ? force : !hdr.classList.contains('open');
  hdr.classList.toggle('open', open);
  const body = hdr.nextElementSibling;
  body.classList.toggle('open', open);
}

async function addModule(subtype) {
  if (!S.currentScript) { toast('请先选择一个脚本', 'warning'); return; }
  const parentPath = S.selectedNodePath || [];
  const r = await API.addNode(S.currentScript, parentPath, subtype);
  if (r.success) {
    S.currentScriptData = r.script;
    renderTree();
    renderMiniFlow(S.selectedNodePath ? getNodeByPath(S.selectedNodePath) : S.currentScriptData?.root);
    toast('模块已添加', 'success');
  } else {
    toast(r.error || '添加失败', 'error');
  }
}

// ═══════════════ TREE EDITOR ═══════════════
function getNodeByPath(path) {
  if (!path.length) return S.currentScriptData?.root;
  let node = S.currentScriptData?.root;
  for (const idx of path) {
    if (!node?.children || !node.children[idx]) return null;
    node = node.children[idx];
  }
  return node;
}

function renderTree() {
  const el = $('#tree-editor');
  const root = S.currentScriptData?.root;
  if (!root) {
    el.innerHTML = '<div class="empty-hint">选择一个脚本以编辑<br>在模块面板中点击模块添加节点</div>';
    return;
  }
  el.innerHTML = '';
  el.appendChild(buildTreeDOM(root, [], 0));
}

function buildTreeDOM(node, path, depth) {
  const wrapper = document.createElement('div');
  wrapper.className = 'tree-node';

  const mod = S.modules.find(m => m.subtype === node.subtype);
  const icon = mod?.icon || '?';
  const label = mod?.label || node.subtype;
  const catClass = 'cat-' + node.type;
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = S.selectedNodePath && arraysEqual(path, S.selectedNodePath);

  const row = document.createElement('div');
  row.className = 'node-row' + (isSelected ? ' selected' : '');
  row.style.paddingLeft = (depth * 16 + 8) + 'px';
  row.onclick = (e) => { e.stopPropagation(); selectNode(path); };

  // expand arrow
  const arrow = document.createElement('span');
  arrow.className = 'node-expand';
  arrow.textContent = hasChildren ? '▼' : '';
  arrow.onclick = (e) => {
    e.stopPropagation();
    const childrenEl = wrapper.querySelector(':scope > .node-children');
    if (childrenEl) {
      childrenEl.classList.toggle('collapsed');
      arrow.textContent = childrenEl.classList.contains('collapsed') ? '▶' : '▼';
    }
  };
  row.appendChild(arrow);

  const iconSpan = document.createElement('span');
  iconSpan.className = 'node-icon ' + catClass;
  iconSpan.textContent = icon;
  row.appendChild(iconSpan);

  const labelSpan = document.createElement('span');
  labelSpan.className = 'node-label ' + catClass;
  labelSpan.textContent = label;
  row.appendChild(labelSpan);

  // config summary
  if (node.config) {
    const entries = Object.entries(node.config).slice(0, 2);
    if (entries.length) {
      const sum = document.createElement('span');
      sum.className = 'node-summary';
      sum.textContent = entries.map(([k,v]) => `${k}=${v}`).join(', ');
      row.appendChild(sum);
    }
  }

  // actions
  const actions = document.createElement('span');
  actions.className = 'node-actions';

  const addBtn = document.createElement('button');
  addBtn.className = 'node-act-btn add';
  addBtn.textContent = '+';
  addBtn.title = '添加子节点';
  addBtn.onclick = (e) => {
    e.stopPropagation();
    selectNode(path);
    // Open first accordion to show modules
    const hdr = $('#module-palette .accordion-header');
    if (hdr) toggleAccordion(hdr, true);
  };
  actions.appendChild(addBtn);

  const upBtn = document.createElement('button');
  upBtn.className = 'node-act-btn';
  upBtn.textContent = '↑';
  upBtn.title = '上移';
  upBtn.onclick = (e) => { e.stopPropagation(); moveNode(path, 'up'); };
  actions.appendChild(upBtn);

  const downBtn = document.createElement('button');
  downBtn.className = 'node-act-btn';
  downBtn.textContent = '↓';
  downBtn.title = '下移';
  downBtn.onclick = (e) => { e.stopPropagation(); moveNode(path, 'down'); };
  actions.appendChild(downBtn);

  const delBtn = document.createElement('button');
  delBtn.className = 'node-act-btn del';
  delBtn.textContent = '✕';
  delBtn.title = '删除';
  delBtn.onclick = (e) => { e.stopPropagation(); deleteNode(path); };
  actions.appendChild(delBtn);

  row.appendChild(actions);
  wrapper.appendChild(row);

  // children
  if (hasChildren) {
    const childrenDiv = document.createElement('div');
    childrenDiv.className = 'node-children';
    node.children.forEach((child, i) => {
      childrenDiv.appendChild(buildTreeDOM(child, [...path, i], depth + 1));
    });
    wrapper.appendChild(childrenDiv);
  }

  return wrapper;
}

function arraysEqual(a, b) {
  if (a.length !== b.length) return false;
  return a.every((v, i) => v === b[i]);
}

function selectNode(path) {
  S.selectedNodePath = path.slice();
  const node = getNodeByPath(path);
  renderTree();
  renderProperties(node);
  renderMiniFlow(node);
}

async function moveNode(path, direction) {
  if (!S.currentScript) return;
  const r = await API.moveNode(S.currentScript, path, direction);
  if (r.success) {
    S.currentScriptData = r.script;
    // adjust selection
    const node = getNodeByPath(path);
    if (node?.parent) {
      const idx = node.parent.children.indexOf(node);
      S.selectedNodePath[path.length - 1] = idx;
    }
    renderTree();
  }
}

async function deleteNode(path) {
  if (!S.currentScript) return;
  if (!confirm('确定删除此节点及其所有子节点吗？')) return;
  const r = await API.deleteNode(S.currentScript, path);
  if (r.success) {
    S.currentScriptData = r.script;
    S.selectedNodePath = null;
    renderTree();
    renderProperties(null);
    renderMiniFlow(null);
    toast('节点已删除', 'success');
  }
}

// ═══════════════ PROPERTIES ═══════════════
function renderProperties(node) {
  const el = $('#properties-content');
  if (!node) {
    el.innerHTML = '<div class="empty-hint">选择一个模块<br>编辑其属性</div>';
    return;
  }

  const mod = S.modules.find(m => m.subtype === node.subtype);
  if (!mod) {
    el.innerHTML = `<div class="empty-hint">未知类型: ${esc(node.subtype)}</div>`;
    return;
  }

  let html = `<div style="font-weight:600;margin-bottom:4px;font-size:12px;color:var(--text);">${mod.icon} ${esc(mod.label)}</div>`;
  html += `<div style="font-size:10px;color:var(--text2);margin-bottom:10px;">${esc(mod.description)}</div>`;

  const schema = mod.config_schema || {};
  for (const [key, defaultVal] of Object.entries(schema)) {
    const val = node.config?.[key] ?? defaultVal ?? '';
    html += `<div class="prop-group">
      <div class="prop-label">${esc(key)}</div>
      <input class="prop-input" data-key="${esc(key)}" value="${esc(String(val))}" onchange="saveConfig('${esc(key)}', this.value)">
    </div>`;
  }

  if (node.subtype === 'click_coord') {
    html += `<button class="btn btn-ghost" style="width:100%;margin-top:8px;" onclick="pickCoordForProp()">📍 拾取坐标</button>`;
  }

  el.innerHTML = html;
}

let _configSaveTimer = null;
function saveConfig(key, value) {
  clearTimeout(_configSaveTimer);
  _configSaveTimer = setTimeout(async () => {
    if (!S.currentScript || !S.selectedNodePath) return;
    const r = await API.updateNodeConfig(S.currentScript, S.selectedNodePath, key, value);
    if (r.success) {
      S.currentScriptData = r.script;
    }
  }, 400);
}

async function pickCoordForProp() {
  const r = await API.pickCoordinate();
  toast('请在屏幕上点击以拾取坐标', 'info');
  // Result comes via socket event 'coordinate_picked'
  S._coordTarget = 'prop';
}

// ═══════════════ MINI FLOW ═══════════════
function renderMiniFlow(node) {
  const el = $('#mini-flow-content');
  if (!node) {
    el.innerHTML = '<div class="empty-hint">未选择模块</div>';
    return;
  }
  el.innerHTML = buildFlowHTML(node);
}

function buildFlowHTML(node) {
  const mod = S.modules.find(m => m.subtype === node.subtype);
  const icon = mod?.icon || '•';
  const label = mod?.label || node.subtype;
  const cls = 'cat-' + node.type;
  let html = `<div class="flow-node"><span class="${cls}">${icon}</span> ${esc(label)}</div>`;
  if (node.children?.length) {
    html += '<div class="flow-arrow">│</div>';
    for (const child of node.children) {
      html += `<div style="margin-left:10px;">${buildFlowHTML(child)}</div>`;
    }
  }
  return html;
}

// ═══════════════ TEMPLATE LIST ═══════════════
function renderTemplateList() {
  const el = $('#template-list');
  if (!S.templates.length) { el.innerHTML = '<div class="empty-hint">暂无模板</div>'; return; }
  el.innerHTML = S.templates.map(t => `
    <div class="script-item" style="justify-content:space-between;">
      <span>🖼 ${esc(t)}</span>
      <span>
        <button class="mini-btn" onclick="useTemplate('${esc(t)}')" title="使用">→</button>
        <button class="mini-btn danger" onclick="delTemplate('${esc(t)}')" title="删除">✕</button>
      </span>
    </div>`).join('');
}

function useTemplate(name) {
  if (!S.selectedNodePath) return toast('请先选择一个节点', 'warning');
  const node = getNodeByPath(S.selectedNodePath);
  if (node && 'template' in (node.config || {})) {
    saveConfig('template', name);
    renderTree();
    toast(`已设置模板: ${name}`, 'success');
  } else {
    toast('当前节点不支持模板属性', 'warning');
  }
}

async function delTemplate(name) {
  if (!confirm(`确定删除模板 "${name}" 吗？`)) return;
  await API.deleteTemplate(name);
  await refreshAll();
  toast('模板已删除', 'success');
}

// ═══════════════ EVENT LOG ═══════════════
function addLog(ts, level, msg) {
  const el = $('#log-entries');
  const line = document.createElement('div');
  line.className = `log-entry ${(level || 'info').toLowerCase()}`;
  line.textContent = `[${ts}] ${level} ${msg}`;
  el.appendChild(line);
  S.logCount++;
  $('#log-count').textContent = S.logCount;

  // auto-scroll if near bottom
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 60) {
    el.scrollTop = el.scrollHeight;
  }

  // cap at 500
  while (el.children.length > 500) el.firstElementChild.remove();
}

// ═══════════════ DASHBOARD ═══════════════
function toggleDashboard(show) {
  const overlay = $('#dashboard-overlay');
  if (show === undefined) show = overlay.classList.contains('hidden');
  overlay.classList.toggle('hidden', !show);
  if (show) {
    S.socket?.emit('subscribe_dashboard');
  } else {
    S.socket?.emit('unsubscribe_dashboard');
  }
}

function updateDashboard(data) {
  const el = $('#dashboard-cards');
  const summary = $('#dashboard-summary');
  if (!data.runners || !data.runners.length) {
    el.innerHTML = '<div class="empty-hint">没有脚本在运行</div>';
    summary.textContent = '';
    return;
  }
  const running = data.runners.filter(r => r.state === 'running').length;
  summary.textContent = `脚本: ${running}/${data.runners.length} | 线程: ${data.runners.length}/8`;

  el.innerHTML = data.runners.map(r => `
    <div class="dash-card ${r.state}">
      <div class="dash-name">${esc(r.name)}</div>
      <div class="dash-info">
        状态: ${r.state} | 匹配: ${r.match_count}次 | 运行: ${r.runtime_seconds?.toFixed(0) || 0}秒
        ${r.error ? `<br><span style="color:var(--red)">错误: ${esc(r.error)}</span>` : ''}
      </div>
    </div>`).join('');
}

// ═══════════════ MODALS ═══════════════
function showModal(html) {
  const overlay = $('#modal-overlay');
  $('#modal-body').innerHTML = html;
  overlay.classList.remove('hidden');
}

function hideModal() {
  $('#modal-overlay').classList.add('hidden');
}
$('#modal-overlay').addEventListener('click', (e) => {
  if (e.target === $('#modal-overlay')) hideModal();
});

// New project
function showNewProjectModal() {
  showModal(`
    <div class="modal-title">📁 新建项目</div>
    <input class="modal-input" id="new-proj-name" placeholder="项目名称">
    <input class="modal-input" id="new-proj-dir" placeholder="项目目录 (例如: C:\\MyProject)">
    <div class="modal-btn-row">
      <button class="btn btn-ghost" onclick="hideModal()">取消</button>
      <button class="btn btn-green" onclick="createProject()">创建</button>
    </div>
  `);
}
async function createProject() {
  const name = $('#new-proj-name').value.trim();
  const directory = $('#new-proj-dir').value.trim();
  if (!name || !directory) return toast('请填写项目名称和目录', 'warning');
  // Use name as subdirectory
  const fullPath = directory.endsWith(name) ? directory : directory + '/' + name;
  const r = await API.projectNew(name, fullPath);
  if (r.success) {
    hideModal();
    await refreshAll();
    toast('项目已创建', 'success');
  } else {
    toast(r.error || '创建失败', 'error');
  }
}

// Open project
function showOpenProjectModal() {
  showModal(`
    <div class="modal-title">📂 打开项目</div>
    <input class="modal-input" id="open-proj-dir" placeholder="项目目录路径">
    <div class="modal-btn-row">
      <button class="btn btn-ghost" onclick="hideModal()">取消</button>
      <button class="btn btn-blue" onclick="openProject()">打开</button>
    </div>
  `);
}
async function openProject() {
  const directory = $('#open-proj-dir').value.trim();
  if (!directory) return toast('请输入项目目录路径', 'warning');
  const r = await API.projectOpen(directory);
  if (r.success) {
    hideModal();
    await refreshAll();
    toast('项目已打开', 'success');
  } else {
    toast(r.error || '打开失败', 'error');
  }
}

// Wizard
function showWizardModal() {
  let step = 0;
  let selTemplate = S.templates[0] || '';
  let actionType = 'click';
  let loopMode = 'always';

  function renderStep() {
    let body = '';
    if (step === 0) {
      body = `<div class="modal-title">第一步：选择触发图像</div>`;
      if (S.templates.length) {
        body += S.templates.map(t => `
          <label class="modal-radio"><input type="radio" name="wiz-tmpl" value="${esc(t)}" ${t === selTemplate ? 'checked' : ''} onchange="selTemplate=this.value"> ${esc(t)}</label>
        `).join('');
      } else {
        body += '<p style="color:var(--text2)">暂无模板，请先在模板库中导入</p>';
      }
    } else if (step === 1) {
      body = `<div class="modal-title">第二步：选择执行动作</div>
        <label class="modal-radio"><input type="radio" name="wiz-act" value="click" ${actionType==='click'?'checked':''} onchange="actionType=this.value"> 🖱 点击图像中心</label>
        <label class="modal-radio"><input type="radio" name="wiz-act" value="key" ${actionType==='key'?'checked':''} onchange="actionType=this.value"> ⌨ 按下键盘按键</label>
        <label class="modal-radio"><input type="radio" name="wiz-act" value="click_coord" ${actionType==='click_coord'?'checked':''} onchange="actionType=this.value"> 🎯 点击固定坐标</label>
        ${actionType==='key' ? '<input class="modal-input" id="wiz-key" placeholder="按键名称 (例如: f1, enter)" value="f1">' : ''}
      `;
    } else if (step === 2) {
      body = `<div class="modal-title">第三步：设置运行方式</div>
        <label class="modal-radio"><input type="radio" name="wiz-loop" value="always" ${loopMode==='always'?'checked':''} onchange="loopMode=this.value"> 持续检测（图像可见时循环执行）</label>
        <label class="modal-radio"><input type="radio" name="wiz-loop" value="once" ${loopMode==='once'?'checked':''} onchange="loopMode=this.value"> 仅执行一次</label>
        <div class="prop-label" style="margin-top:12px;">检测间隔 (毫秒)</div>
        <input class="modal-input" id="wiz-tick" value="500" type="number">
      `;
    }

    // Read current values from DOM back to closures
    body += `<div class="modal-btn-row">
      ${step > 0 ? '<button class="btn btn-ghost" onclick="step--; renderStep()">上一步</button>' : ''}
      ${step < 2 ? '<button class="btn btn-blue" onclick="step++; renderStep()">下一步</button>'
                 : '<button class="btn btn-green" onclick="finishWizard()">生成脚本</button>'}
    </div>`;
    $('#modal-body').innerHTML = body;

    // Re-bind global functions for modal interaction
    window.step = step;
    window.renderStep = renderStep;
    window.selTemplate = selTemplate;
    window.actionType = actionType;
    window.loopMode = loopMode;
  }

  window.step = 0;
  window.renderStep = renderStep;
  window.selTemplate = selTemplate;
  window.actionType = actionType;
  window.loopMode = loopMode;
  window.finishWizard = async function() {
    if (!selTemplate) { toast('请选择一个模板', 'warning'); return; }
    const data = {
      name: `向导脚本 ${(S.scripts?.length || 0) + 1}`,
      template: selTemplate,
      action_type: actionType,
      action_config: actionType === 'key' ? { key: $('#wiz-key')?.value || 'f1' } : {},
      loop_mode: loopMode,
      tick_ms: parseInt($('#wiz-tick')?.value || 500),
    };
    const r = await API.wizardGenerate(data);
    if (r.success) {
      hideModal();
      await refreshAll();
      selectScript(r.name);
      toast('脚本已生成', 'success');
    }
  };

  showModal('<div id="wizard-body"></div>');
  renderStep();
}

// Window selector
async function showWindowSelector() {
  const r = await API.listWindows();
  const windows = r.windows || [];
  showModal(`
    <div class="modal-title">🔍 选择目标窗口</div>
    <input class="modal-input" id="win-filter" placeholder="输入过滤..." oninput="filterWindows()">
    <div style="max-height:300px;overflow-y:auto;" id="win-list">
      ${windows.map((w,i) => `
        <div class="script-item win-opt" data-name="${esc(w)}" onclick="document.getElementById('script-window').value='${esc(w)}'; hideModal();">
          ${esc(w.length > 50 ? w.slice(0,47)+'...' : w)}
        </div>`).join('')}
    </div>
    <script>window.filterWindows = function() {
      const q = document.getElementById('win-filter').value.toLowerCase();
      document.querySelectorAll('.win-opt').forEach(el => {
        el.style.display = el.dataset.name.toLowerCase().includes(q) ? '' : 'none';
      });
    }</script>
  `);
}

// ═══════════════ REFRESH ═══════════════
async function refreshAll() {
  const stateR = await API.projectState();
  if (stateR.success) {
    S.project = stateR;
    S.scripts = (stateR.scripts || []).map(s => ({ name: s.name, enabled: s.enabled }));
    S.templates = stateR.templates || [];
  }
  const modR = await API.getModules();
  if (modR.modules) S.modules = modR.modules;

  renderScriptList();
  renderModulePalette();
  renderTemplateList();

  if (S.currentScript) {
    const r = await API.getScript(S.currentScript);
    if (r.success) {
      S.currentScriptData = r.script;
      renderScriptMeta();
      renderTree();
    }
  }
}

// ═══════════════ SOCKETIO ═══════════════
function initSocket() {
  S.socket = io({ transports: ['websocket', 'polling'] });

  S.socket.on('connect', () => {
    console.log('Socket connected:', S.socket.id);
  });

  S.socket.on('runtime_state', (data) => {
    updateDashboard(data);
    if (data.state === 'idle' || data.state === 'stopped') {
      S.running = false;
      setStatus('idle');
    } else if (data.state === 'running') {
      S.running = true;
      setStatus('running');
    } else if (data.state === 'paused') {
      setStatus('paused');
    }
  });

  S.socket.on('runner_log', (data) => {
    if (data.entries) {
      data.entries.forEach(e => {
        const ts = new Date(e.ts * 1000).toLocaleTimeString('zh-CN', { hour12: false });
        addLog(ts, e.level || 'info', `[${data.script_name}] ${e.msg}`);
      });
    }
  });

  S.socket.on('template_captured', (data) => {
    toast(`模板已保存: ${data.name} (${data.width}x${data.height})`, 'success');
    refreshAll();
  });

  S.socket.on('coordinate_picked', (data) => {
    toast(`坐标已拾取: (${data.x}, ${data.y}) RGB(${data.rgb?.join(',')})`, 'info');
    // If from properties panel, fill in fields
    if (S.selectedNodePath && S.currentScript) {
      const node = getNodeByPath(S.selectedNodePath);
      if (node && 'x' in (node.config || {})) {
        saveConfig('x', data.x);
        saveConfig('y', data.y);
        renderTree();
        renderProperties(getNodeByPath(S.selectedNodePath));
      }
    }
  });

  S.socket.on('error', (data) => {
    toast(data.message || '发生错误', 'error');
  });
}

// ═══════════════ TOOLBAR WIRING ═══════════════
function wireToolbar() {
  $('#btn-run').onclick = async () => {
    if (S.running) return toast('脚本已在运行', 'warning');
    await API.runtimeStart();
    toast('脚本已启动', 'success');
    toggleDashboard(true);
    S.running = true;
    setStatus('running');
  };
  $('#btn-stop').onclick = async () => {
    await API.runtimeStop();
    toast('脚本已停止', 'info');
    setStatus('stopped');
    S.running = false;
  };
  $('#btn-pause').onclick = async () => {
    await API.runtimePause();
    toast('已切换暂停状态', 'info');
  };
  $('#btn-emergency').onclick = async () => {
    if (!confirm('确定要紧急停止所有脚本吗？')) return;
    await API.runtimeEmergency();
    toast('紧急停止已执行', 'warning');
    setStatus('stopped');
    S.running = false;
  };
  $('#btn-capture').onclick = async () => {
    if (!S.project) return toast('请先创建或打开项目', 'warning');
    const r = await API.captureTemplate();
    toast(r.message || '已在桌面开启截图工具', 'info');
  };
  $('#btn-coord').onclick = async () => {
    const r = await API.pickCoordinate();
    toast(r.message || '请在屏幕上点击以拾取坐标', 'info');
  };
  $('#btn-wizard').onclick = () => {
    if (!S.project) return toast('请先创建或打开项目', 'warning');
    showWizardModal();
  };
  $('#btn-project-open').onclick = () => {
    if (S.project) showOpenProjectModal();
    else showNewProjectModal();
  };
  $('#btn-project-save').onclick = async () => {
    if (!S.project) return toast('没有打开的项目', 'warning');
    await API.projectSave();
    toast('项目已保存', 'success');
  };
  $('#btn-new-script').onclick = async () => {
    if (!S.project) return toast('请先创建或打开项目', 'warning');
    const name = prompt('脚本名称:', '新脚本');
    if (!name) return;
    await API.createScript(name);
    await refreshAll();
    selectScript(name);
    toast('脚本已创建', 'success');
  };
  $('#btn-upload-template').onclick = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/png,image/jpeg,image/bmp';
    input.onchange = async () => {
      if (!input.files[0]) return;
      const form = new FormData();
      form.append('file', input.files[0]);
      const r = await fetch('/api/templates/upload', { method: 'POST', body: form });
      const data = await r.json();
      if (data.success) {
        await refreshAll();
        toast(`模板 ${data.name} 已导入`, 'success');
      }
    };
    input.click();
  };
  $('#btn-script-delete').onclick = async () => {
    if (!S.currentScript) return;
    if (!confirm(`确定删除脚本 "${S.currentScript}" 吗？`)) return;
    await API.deleteScript(S.currentScript);
    S.currentScript = null;
    S.currentScriptData = null;
    S.selectedNodePath = null;
    await refreshAll();
    renderTree();
    renderProperties(null);
    renderMiniFlow(null);
    renderScriptMeta();
    toast('脚本已删除', 'success');
  };
  $('#btn-select-window').onclick = showWindowSelector;
  $('#btn-clear-log').onclick = () => {
    $('#log-entries').innerHTML = '';
    S.logCount = 0;
    $('#log-count').textContent = '0';
  };
  $('#btn-toggle-log').onclick = () => {
    const panel = $('#bottom-panel');
    const btn = $('#btn-toggle-log');
    panel.classList.toggle('collapsed');
    btn.textContent = panel.classList.contains('collapsed') ? '▲' : '▼';
  };
  $('#btn-close-dashboard').onclick = () => toggleDashboard(false);
  $('#dashboard-overlay').addEventListener('click', (e) => {
    if (e.target === $('#dashboard-overlay')) toggleDashboard(false);
  });
  $('#log-header').style.cursor = 'pointer';
  $('#log-header').onclick = (e) => {
    if (e.target.tagName === 'BUTTON') return;
    const panel = $('#bottom-panel');
    panel.classList.toggle('collapsed');
    $('#btn-toggle-log').textContent = panel.classList.contains('collapsed') ? '▲' : '▼';
  };
}

// ═══════════════ INIT ═══════════════
async function init() {
  initSocket();
  wireToolbar();

  // Wait for socket connection
  await new Promise(r => {
    const check = () => S.socket?.connected ? r() : setTimeout(check, 100);
    check();
  });

  // Load modules immediately (no project needed)
  const modR = await API.getModules();
  if (modR.modules) S.modules = modR.modules;
  renderModulePalette();

  // Try to load project state
  await refreshAll();

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 's') { e.preventDefault(); $('#btn-project-save').click(); }
    if (e.key === 'Escape') hideModal();
    if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); $('#btn-run').click(); }
  });

  // Auto-shutdown when browser closes
  window.addEventListener('beforeunload', () => {
    if (S.socket?.connected) {
      S.socket.emit('shutdown');
    }
  });

  console.log('AutoVision UI initialized');
}

init();
