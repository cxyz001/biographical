const fs = require('node:fs');
const path = require('node:path');

const source = path.join(__dirname, '01-AI大模型零基础教程.md');
const target = path.join(__dirname, '01-AI大模型应用工程.html');
const markdown = JSON.stringify(fs.readFileSync(source, 'utf8')).replace(/</g, '\\u003c');
const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI 大模型零基础教程 · 从聊天到 Agent</title>
<style>
*{box-sizing:border-box}body{margin:0;color:#202a27;background:#fff;font:16px/1.85 system-ui,"Microsoft YaHei",sans-serif;letter-spacing:0}
header{border-bottom:1px solid #d9e2dd;padding:12px 24px;display:flex;gap:16px;align-items:center;flex-wrap:wrap;background:#f4f8f5}
header strong{color:#166047}a{color:#146a50;text-underline-offset:3px}main{max-width:980px;margin:auto;padding:24px 32px 80px;overflow-wrap:anywhere}
details{border-bottom:1px solid #dce4df;padding:16px 0}summary{cursor:pointer;font-weight:600;color:#166047}details p{padding:0 16px}
h1{font-size:32px;line-height:1.4}h2{font-size:25px;border-bottom:1px solid #dce4df;padding-bottom:10px;margin-top:48px}h3{font-size:20px;margin-top:32px}
blockquote{border-left:3px solid #4b8b70;margin:20px 0;padding:8px 20px;background:#f5f8f6}blockquote p{margin:4px 0}
pre{overflow:auto;background:#f3f5f4;padding:18px;border:1px solid #dce2df;border-radius:4px;font:14px/1.7 Consolas,monospace}code{font-family:Consolas,monospace}p code,li code,td code{background:#f0f3f1;padding:2px 4px}
.table-scroll{overflow:auto;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:14px;min-width:640px}th,td{border:1px solid #d6dfd9;padding:10px 12px;text-align:left;vertical-align:top}th{background:#edf4ef}tr:nth-child(even){background:#fafcfb}
hr{border:0;border-top:1px solid #dce4df;margin:36px 0}.diagram{border:1px solid #cbd9d0;margin:24px 0;border-radius:4px;overflow:hidden}
.diagram-bar{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:8px 12px;background:#eff5f1;border-bottom:1px solid #d5dfd8}.diagram-bar strong{font-size:14px;margin-right:auto}
button{display:inline-flex;align-items:center;justify-content:center;min-height:36px;min-width:36px;padding:6px 10px;border:1px solid #baccc0;border-radius:4px;background:white;color:#174b37;cursor:pointer;font:inherit;line-height:1.2}button:hover{background:#dfeee4}button:focus-visible,a:focus-visible{outline:3px solid #176f54;outline-offset:3px}button:disabled{opacity:.4;cursor:default}.percent{font-size:13px;min-width:48px;text-align:center}
.viewport{overflow:auto;max-height:760px;padding:20px;background:#fff}.canvas{margin:auto}.canvas svg{display:block;width:100%!important;height:100%!important;max-width:none!important}
dialog{width:96vw;max-width:none;height:94vh;max-height:94vh;padding:0;border:1px solid #a9beb0;border-radius:4px}dialog::backdrop{background:#17251bd9}dialog[open]{display:flex;flex-direction:column}dialog .viewport{flex:1;max-height:none;min-height:0}dialog .diagram-bar{flex:none}
.error{padding:16px;color:#9b2424;background:#fff3f0}#loading{padding:24px}#top-link{white-space:nowrap}
@media(max-width:640px){main{padding:16px 14px 48px}header{padding:12px 14px}h1{font-size:26px}h2{font-size:22px}.viewport{padding:12px;max-height:560px}.diagram-bar{padding:8px}.diagram-bar strong{width:100%}dialog{width:100vw;height:96vh;max-height:96vh}}
@media print{header,.diagram-bar{display:none}.viewport{max-height:none;overflow:visible}.canvas{width:100%!important;height:auto!important}.canvas svg{height:auto!important}main{max-width:none;padding:0}.diagram{break-inside:avoid}h2,h3{break-after:avoid}}
</style>
</head>
<body>
<header id="top"><strong>AI 大模型零基础教程</strong><a href="#学习路线">学习路线</a><a href="#第7课agent能围绕目标选择下一步的助手">认识 Agent</a><a href="#第8课第一次落地从小助手开始">动手实践</a><a href="01-AI大模型应用工程.md">进阶参考</a><a id="top-link" href="#top">↑ 顶部</a></header>
<div id="loading" role="status">正在加载文档与图形…</div><main id="content"></main>
<dialog id="lightbox" aria-label="图形大图查看"><div class="diagram-bar"><strong id="dialog-title"></strong><span id="modal-tools"></span><button id="close" title="关闭大图 (Esc)" aria-label="关闭大图">✕</button></div><div class="viewport"><div class="canvas"></div></div></dialog>
<script src="https://cdn.jsdelivr.net/npm/marked@15.0.12/marked.min.js"></script>
<script type="module">
const markdown = ${markdown};
const content = document.getElementById('content');
const loading = document.getElementById('loading');
const dialog = document.getElementById('lightbox');
let active = null;
const slug = text => text.toLowerCase().replace(/[^\\p{L}\\p{N}_ -]/gu, '').replace(/ /g, '-');
function makeButton(label, title, action) {
  const button = document.createElement('button');
  button.textContent = label; button.title = title; button.setAttribute('aria-label', title);
  button.addEventListener('click', action); return button;
}
function setupView(canvas, viewport, width, height, tools) {
  let scale = 1;
  const percent = document.createElement('span'); percent.className = 'percent'; percent.setAttribute('aria-live','polite');
  function resize(value) {
    scale = Math.min(4, Math.max(.1, value));
    canvas.style.width = Math.round(width * scale) + 'px';
    canvas.style.height = Math.round(height * scale) + 'px';
    percent.textContent = Math.round(scale * 100) + '%';
  }
  function fit() { resize(Math.min(1, (viewport.clientWidth - 40) / width)); }
  tools.append(makeButton('−', '缩小图形', () => resize(scale / 1.25)), percent,
    makeButton('+', '放大图形', () => resize(scale * 1.25)),
    makeButton('↔', '适应窗口宽度', fit), makeButton('1:1', '原始尺寸', () => resize(1)));
  fit(); return { fit, resize };
}
function openDiagram(svg, width, height, title, trigger) {
  const canvas = dialog.querySelector('.canvas');
  canvas.replaceChildren(svg.cloneNode(true));
  // A clone must not reuse Mermaid marker and label IDs from the inline SVG.
  const prefix = 'modal-' + Date.now() + '-';
  const cloned = canvas.firstElementChild;
  const ids = new Map([...cloned.querySelectorAll('[id]'), cloned].filter(el => el.id).map(el => [el.id, prefix + el.id]));
  for (const el of [cloned, ...cloned.querySelectorAll('*')]) {
    for (const attr of [...el.attributes]) {
      let value = attr.value;
      if (attr.name === 'id') value = ids.get(value) || value;
      else if (attr.name === 'aria-labelledby' || attr.name === 'aria-describedby') value = value.split(' ').map(id => ids.get(id) || id).join(' ');
      else { for (const [id, renamed] of ids) { value = value.split('url(#' + id + ')').join('url(#' + renamed + ')'); if (value === '#' + id) value = '#' + renamed; } }
      el.setAttribute(attr.name, value);
    }
  }
  for (const style of cloned.querySelectorAll('style')) {
    style.textContent = style.textContent.split('#' + svg.id).join('#' + ids.get(svg.id));
  }
  document.getElementById('dialog-title').textContent = title;
  const tools = document.getElementById('modal-tools'); tools.replaceChildren(); tools.style.display = 'contents';
  active = trigger; dialog.showModal();
  setupView(canvas, dialog.querySelector('.viewport'), width, height, tools).resize(1);
  dialog.querySelector('.viewport').scrollTo(0, 0);
}
document.getElementById('close').onclick = () => dialog.close();
dialog.addEventListener('close', () => { active?.focus(); });
try {
  if (!window.marked) throw new Error('Markdown 渲染库加载失败');
  content.innerHTML = marked.parse(markdown);
  for (const heading of content.querySelectorAll('h1,h2,h3')) heading.id = slug(heading.textContent);
  for (const table of content.querySelectorAll('table')) { const wrapper = document.createElement('div'); wrapper.className = 'table-scroll'; table.before(wrapper); wrapper.append(table); }
  loading.textContent = '正文已加载，正在渲染图形…';
  const {default: mermaid} = await import('https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs');
  mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'neutral',flowchart:{useMaxWidth:false},themeVariables:{fontSize:'18px',fontFamily:'system-ui, Microsoft YaHei, sans-serif'}});
  let index = 0;
  for (const code of [...content.querySelectorAll('pre > code.language-mermaid')]) {
    const pre = code.parentElement;
    try {
      const number = ++index;
      const {svg} = await mermaid.render('diagram-' + number, code.textContent);
      const section = document.createElement('section'); section.className = 'diagram';
      const bar = document.createElement('div'); bar.className = 'diagram-bar';
      const title = '图 ' + number;
      const label = document.createElement('strong'); label.textContent = title; bar.append(label);
      const viewport = document.createElement('div'); viewport.className = 'viewport'; viewport.tabIndex = 0; viewport.setAttribute('aria-label', title + '，可滚动');
      const canvas = document.createElement('div'); canvas.className = 'canvas'; canvas.innerHTML = svg;
      viewport.append(canvas); section.append(bar, viewport); pre.replaceWith(section);
      const element = canvas.querySelector('svg'); const box = element.viewBox.baseVal;
      const width = box.width || 1000, height = box.height || 600;
      setupView(canvas, viewport, width, height, bar);
      const open = makeButton('⛶', '查看大图', () => openDiagram(element,width,height,title,open)); bar.append(open);
    } catch (error) {
      const message = document.createElement('p'); message.className = 'error'; message.textContent = '图形渲染失败，保留 Mermaid 源码：' + error.message; pre.before(message);
    }
  }
  loading.remove();
  if (location.hash) document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView();
} catch(error) {
  loading.className = 'error'; loading.textContent = error.message + '。请联网后刷新；也可打开同目录 Markdown 原文。';
  if (!content.textContent) { const pre = document.createElement('pre'); pre.textContent = markdown; content.append(pre); }
}
</script>
</body>
</html>`;
fs.writeFileSync(target, html, 'utf8');
console.log('Generated ' + target);
