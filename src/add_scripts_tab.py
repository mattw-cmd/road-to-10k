"""Add the Scripts tab (this week's scripts, teleprompter, copy caption) to template.html. Idempotent."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = 'template.html'
s = open(p, encoding='utf-8').read()
if 'tab-scripts' in s:
    print('scripts tab already present'); sys.exit(0)

def swap(src, old, new, label):
    assert old in src, 'anchor not found: ' + label
    return src.replace(old, new, 1)

# CSS
s = swap(s, ".small{font-size:12.5px;color:var(--muted)}",
""".small{font-size:12.5px;color:var(--muted)}
.script{font-size:16px;line-height:1.55;white-space:pre-line;padding:12px 14px;border-radius:12px;background:var(--surface2);margin-top:8px}
.script .hookline{font-weight:600}
.slides{margin-top:8px;display:flex;flex-direction:column;gap:6px}
.slide{display:grid;grid-template-columns:28px 1fr;gap:10px;padding:8px 0;border-top:1px solid var(--line);font-size:14px}
.slide:first-child{border-top:0}
.slide .n{font-weight:700;color:var(--accent);font-size:12px;padding-top:2px}
.slide .h{font-weight:600;color:var(--accent);font-size:13px}
.kv{display:grid;grid-template-columns:96px 1fr;gap:6px 10px;font-size:13px;margin-top:8px}
.kv .k{color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-size:11px;padding-top:2px}
details.cap{margin-top:8px}
details.cap summary{cursor:pointer;font-weight:600;font-size:13px;color:var(--accent)}
details.cap pre{white-space:pre-wrap;font:inherit;font-size:13.5px;background:var(--surface2);padding:10px 12px;border-radius:10px;margin:6px 0 0}
.btnrow{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.prompter{position:fixed;inset:0;z-index:40;background:var(--bg);color:var(--ink);display:flex;flex-direction:column}
.prompter .bar{display:flex;gap:8px;align-items:center;justify-content:space-between;padding:calc(10px + env(safe-area-inset-top,0px)) 14px 10px;border-bottom:1px solid var(--line)}
.prompter .txt{flex:1;overflow:auto;padding:24px 20px calc(40vh + env(safe-area-inset-bottom,0px));white-space:pre-line;line-height:1.5;font-weight:500;text-wrap:pretty}
.prompter .txt p{margin:0 0 .9em}""", 'css')

# section + tab button
s = swap(s, '  <section id="tab-hooks" hidden></section>', '  <section id="tab-hooks" hidden></section>\n  <section id="tab-scripts" hidden></section>', 'section')
s = swap(s, 'Hooks</button>\n</nav>',
'Hooks</button>\n  <button class="tab" role="tab" data-tab="scripts" aria-selected="false"><svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>Scripts</button>\n</nav>', 'tab button')

# render function, inserted before header render
render = r"""// ---------- SCRIPTS (this week) ----------
async function copyText(t,label){try{await navigator.clipboard.writeText(t);toast((label||'Copied')+' to clipboard');}catch(e){toast('Copy failed, long-press to select instead');}}
function slidesText(sc){return (sc.slides||[]).map((sl,i)=>`${i===0?'Cover':'Slide '+(i+1)} · ${sl[0]}\n${sl[1]}`).join('\n\n');}
let prompterEl=null,prompterSize=30;
function openPrompter(s){
  closePrompter();
  prompterEl=el('div','prompter');prompterEl.setAttribute('role','dialog');prompterEl.setAttribute('aria-label','Teleprompter');
  const paras=String(s.script.spoken||'').split(/\n\s*\n/).map(x=>`<p>${esc(x)}</p>`).join('');
  prompterEl.innerHTML=`<div class="bar"><div><div style="font-weight:700">${esc(s.title)}</div><div class="small num">${s.script.words||''} words · about ${s.script.seconds||''} sec</div></div><div style="display:flex;gap:6px"><button class="btn small" id="pMinus" aria-label="Smaller text">A&minus;</button><button class="btn small" id="pPlus" aria-label="Larger text">A+</button><button class="btn small primary" id="pClose">Close</button></div></div><div class="txt" id="pTxt" style="font-size:${prompterSize}px">${paras}</div>`;
  document.body.appendChild(prompterEl);
  const txt=prompterEl.querySelector('#pTxt');
  prompterEl.querySelector('#pClose').onclick=closePrompter;
  prompterEl.querySelector('#pMinus').onclick=()=>{prompterSize=Math.max(18,prompterSize-3);txt.style.fontSize=prompterSize+'px';};
  prompterEl.querySelector('#pPlus').onclick=()=>{prompterSize=Math.min(56,prompterSize+3);txt.style.fontSize=prompterSize+'px';};
  document.addEventListener('keydown',escClose);
}
function escClose(e){if(e.key==='Escape')closePrompter();}
function closePrompter(){if(prompterEl){prompterEl.remove();prompterEl=null;document.removeEventListener('keydown',escClose);}}
function renderScripts(){
  const root=document.getElementById('tab-scripts'); root.innerHTML='';
  const today=todayISO(); const w=weekFor(today);
  const slots=Object.values(state.slots).filter(s=>s.date>=w.start&&s.date<=w.end);
  const withScript=slots.filter(s=>s.script&&(s.script.spoken||s.script.slides)).sort((a,b)=>(a.script.order||99)-(b.script.order||99)||(a.date<b.date?-1:1));
  const head=el('div','card');
  head.innerHTML=`<h2 style="margin-top:0">Scripts · week ${w.n}</h2><h3>${fmtDM(w.start)} to ${fmtDM(w.end)}${w.batch?' · batch '+fmtShort(w.batch):''}</h3><div class="small">${withScript.length} of ${slots.length} slots have a script. In filming order: Lane A at the desk first, then Lane B, then carousels to build. New scripts arrive with each Sunday import.</div>${w.filmingRules?`<div class="small" style="margin-top:8px;color:var(--ink2)">${esc(w.filmingRules)}</div>`:''}`;
  root.appendChild(head);
  if(!withScript.length){root.appendChild(el('div','card empty','No scripts loaded for this week yet. Import the Sunday file, or check the shot list doc in Drive.'));}
  withScript.forEach(s=>{
    const sc=s.script; const isReel=s.format==='Reel';
    const c=el('div','card'); c.id='script-'+s.id;
    let h=`<div class="meta" style="display:flex;gap:6px;flex-wrap:wrap;align-items:center"><span class="tag num">${sc.order?sc.order+'.':''} ${esc(s.id)}</span><span class="chip fmt">${esc(s.format)}${s.lane&&s.lane!=='-'?' · Lane '+esc(s.lane):''}</span>${pillarChip(s.pillar)}<span class="chip ${esc(s.kind)}">${esc(s.kind)}</span><button class="chip ${esc(s.status)}" data-open="${esc(s.id)}" style="cursor:pointer">${esc(s.status)}</button></div>
    <h3 style="margin-top:8px">${esc(s.title)}</h3><div class="small num">Posts ${fmtShort(s.date)} ${esc(s.time)}</div>
    ${sc.setup?`<div class="small" style="margin-top:6px;color:var(--ink2)">${esc(sc.setup)}</div>`:''}`;
    if(isReel){
      h+=`<div class="script"><span class="hookline">${esc(s.hook)}</span>${sc.spoken?'\n\n'+esc(sc.spoken.replace(s.hook,'').replace(/^\s+/,'')):''}</div>
      <div class="kv">${sc.words?`<span class="k">Length</span><span class="num">${sc.words} words, about ${sc.seconds} seconds</span>`:''}${sc.onScreen?`<span class="k">On screen</span><span>${esc(sc.onScreen)}</span>`:''}${sc.numbers?`<span class="k">Numbers</span><span>${esc(sc.numbers)}</span>`:''}${sc.disclaimerText?`<span class="k">Disclaimer</span><span><i>${esc(sc.disclaimerText)}</i></span>`:''}${s.cta?`<span class="k">CTA</span><span>${esc(s.cta)}</span>`:''}</div>
      <div class="btnrow"><button class="btn primary" data-prompt="${esc(s.id)}">Teleprompter</button><button class="btn" data-copy="script" data-id="${esc(s.id)}">Copy script</button><button class="btn" data-copy="caption" data-id="${esc(s.id)}">Copy caption</button></div>`;
    }else{
      h+=`<div class="slides">${(sc.slides||[]).map((sl,i)=>`<div class="slide"><span class="n num">${i===0?'C':i+1}</span><div><div class="h">${esc(sl[0])}</div><div>${esc(sl[1])}</div></div></div>`).join('')}</div>
      <div class="kv">${sc.disclaimerText?`<span class="k">Disclaimer</span><span><i>${esc(sc.disclaimerText)}</i></span>`:''}${s.cta?`<span class="k">CTA</span><span>${esc(s.cta)}</span>`:''}</div>
      <div class="btnrow"><button class="btn" data-copy="slides" data-id="${esc(s.id)}">Copy slide copy</button><button class="btn" data-copy="caption" data-id="${esc(s.id)}">Copy caption</button></div>`;
    }
    if(sc.caption) h+=`<details class="cap"><summary>Caption</summary><pre>${esc(sc.caption)}</pre></details>`;
    c.innerHTML=h; root.appendChild(c);
  });
  const missing=slots.filter(s=>!withScript.includes(s));
  if(withScript.length&&missing.length){const m=el('div','card');m.innerHTML=`<h3>No script yet</h3>`+missing.map(s=>`<div class="small" style="padding:4px 0">${esc(s.id)} · ${esc(s.title)} · ${fmtDM(s.date)}</div>`).join('');root.appendChild(m);}
  if(w.storyClips&&w.storyClips.length){const sc=el('div','card');sc.innerHTML=`<h3>Story clips, ten seconds each</h3>`+w.storyClips.map((t,i)=>`<div class="slide"><span class="n num">${i+1}</span><div>${esc(t)}</div></div>`).join('');root.appendChild(sc);}
  root.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>openSheet(b.getAttribute('data-open')));
  root.querySelectorAll('[data-prompt]').forEach(b=>b.onclick=()=>openPrompter(state.slots[b.dataset.prompt]));
  root.querySelectorAll('[data-copy]').forEach(b=>b.onclick=()=>{const s=state.slots[b.dataset.id];const sc=s.script||{};const k=b.dataset.copy;copyText(k==='caption'?sc.caption||'':k==='slides'?slidesText(sc):(s.hook+'\n\n'+(sc.spoken||'')),k==='caption'?'Caption copied':k==='slides'?'Slide copy copied':'Script copied');});
}

// ---------- header ----------"""
s = swap(s, "// ---------- header ----------", render, 'render insert')

# tabs list + renderAll
s = swap(s, "['week','log','growth','pillars','hooks'].forEach(k=>document.getElementById('tab-'+k).hidden=(k!==t));",
           "['week','log','growth','pillars','hooks','scripts'].forEach(k=>document.getElementById('tab-'+k).hidden=(k!==t));", 'tabs list')
s = swap(s, "function renderAll(){renderHeader();renderWeek();renderLog();renderGrowth();renderPillars();renderHooks();}",
           "function renderAll(){renderHeader();renderWeek();renderLog();renderGrowth();renderPillars();renderHooks();renderScripts();}", 'renderAll')

# Today card: open script button
s = swap(s, """<div style="margin-top:8px"><button class="btn small primary" data-open="${esc(s.id)}">Update status or numbers</button></div>""",
           """<div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn small primary" data-open="${esc(s.id)}">Update status or numbers</button>${s.script?`<button class="btn small" data-script="${esc(s.id)}">Open script</button>`:''}</div>""", 'today button')
s = swap(s, "  root.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>openSheet(b.getAttribute('data-open')));\n}\n\n// ---------- LOG ----------",
           "  root.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>openSheet(b.getAttribute('data-open')));\n  root.querySelectorAll('[data-script]').forEach(b=>b.onclick=()=>{showTab('scripts');const t=document.getElementById('script-'+b.dataset.script);if(t)t.scrollIntoView({block:'start'});});\n}\n\n// ---------- LOG ----------", 'today script handler')

# slot merge on import: script objects are part of slot docs already. Nothing else.
assert "—" not in s
open(p, 'w', encoding='utf-8').write(s)
print('scripts tab added')
