"""Merge Pillars + Hooks into an Insights tab, add a News tab (curated searches, sources, news bank), the locked rhythm card,
retired-slot cleanup, and news in export/import. Idempotent on template.html."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = 'template.html'
s = open(p, encoding='utf-8').read()
if 'tab-news' in s:
    print('news tab already present'); sys.exit(0)

def swap(src, old, new, label):
    assert old in src, 'anchor not found: ' + label
    return src.replace(old, new, 1)

# ---- sections: insights wrapper holds pillars + hooks ----
s = swap(s, '  <section id="tab-pillars" hidden></section>\n  <section id="tab-hooks" hidden></section>',
'''  <section id="tab-insights" hidden>
    <div class="seg" style="margin:14px 0 4px" id="insSeg"><button data-v="pillars" aria-pressed="true">Pillars</button><button data-v="hooks" aria-pressed="false">Hooks</button></div>
    <div id="tab-pillars"></div>
    <div id="tab-hooks" hidden></div>
  </section>
  <section id="tab-news" hidden></section>''', 'sections')

# ---- tab buttons: replace Pillars + Hooks with Insights, add News ----
s = swap(s, '''  <button class="tab" role="tab" data-tab="pillars" aria-selected="false"><svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/></svg>Pillars</button>
  <button class="tab" role="tab" data-tab="hooks" aria-selected="false"><svg viewBox="0 0 24 24"><path d="M12 3v10a4 4 0 1 1-4-4"/><path d="M12 3c3 0 5 2 5 4"/></svg>Hooks</button>''',
'''  <button class="tab" role="tab" data-tab="insights" aria-selected="false"><svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/></svg>Insights</button>
  <button class="tab" role="tab" data-tab="news" aria-selected="false"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>News</button>''', 'tab buttons')

# ---- CSS ----
s = swap(s, ".small{font-size:12.5px;color:var(--muted)}",
""".small{font-size:12.5px;color:var(--muted)}
.linkrow{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 0;border-top:1px solid var(--line);font-size:14px;text-decoration:none;color:var(--ink)}
.linkrow:first-of-type{border-top:0}
.linkrow .r{color:var(--accent);font-weight:700;flex:none}
.linkrow .n{font-size:12px;color:var(--muted)}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 4px}
.chips button{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:6px 11px;font-size:12.5px;font-weight:600;color:var(--ink2)}
.chips button[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.newsitem{padding:10px 0;border-top:1px solid var(--line)}
.newsitem:first-child{border-top:0}
.newsitem .t{font-weight:600;font-size:14.5px}
.newsitem .m{font-size:13px;color:var(--ink2);margin-top:3px}
.rhythm{display:grid;grid-template-columns:44px 1fr auto;gap:8px 10px;font-size:13px;align-items:center}
.rhythm .d{font-weight:700;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.05em}""", 'css')

# ---- state: news bank + insights view ----
s = swap(s, "growthRange:'8w', pillarMetric:'score' };", "growthRange:'8w', pillarMetric:'score', insightsView:'pillars', news:[], newsFilter:0 };", 'state')

# ---- week tab: locked rhythm card after compliance card ----
s = swap(s, "  root.appendChild(comp);\n\n  // review card",
"""  root.appendChild(comp);

  if(S.template&&S.template.length){const rc=el('div','card');rc.innerHTML=`<h2 style="margin-top:0">The locked rhythm</h2><div class="rhythm">${S.template.map(t=>`<span class="d">${esc(t.day)}</span><span><b>${esc(t.format)}${t.lane&&t.lane!=='-'?' '+esc(t.lane):''}</b> &middot; ${esc((PILLARS[t.pillar]||{}).name||'')}<div class="small">${esc(t.note||'')}</div></span><span class="small num">${esc(t.time)}</span>`).join('')}</div><div class="small" style="margin-top:8px">${esc(S.templateRule||'')}</div>`;root.appendChild(rc);}

  // review card""", 'rhythm card')

# themes: only show planned horizon
s = swap(s, "const tm=el('div','themes'); tm.innerHTML=`<h2>Next eight weeks</h2>`;", "const tm=el('div','themes'); tm.innerHTML=`<h2>Ahead</h2>`;", 'themes heading')
s = swap(s, "WEEKS().slice(Math.max(0,weekFor(today).n-1)).slice(0,8).forEach(pw=>{", "WEEKS().slice(Math.max(0,weekFor(today).n-1)).slice(0,4).forEach(pw=>{", 'themes slice')

# ---- News tab render + insights toggle, inserted before header render ----
render = r"""// ---------- NEWS (curated searches, sources, news bank) ----------
function newsBank(){return Array.isArray(state.news)?state.news:[];}
function renderNews(){
  const root=document.getElementById('tab-news'); root.innerHTML='';
  const N=S.news||{searches:[],sources:[]};
  const f=state.newsFilter;
  const head=el('div','card');
  head.innerHTML=`<h2 style="margin-top:0">Curated search</h2><div class="small">${esc(N.angleTest||'')}</div>
  <div class="chips">${[0,1,2,3,4,5].map(n=>`<button data-f="${n}" aria-pressed="${f===n}">${n===0?'All':esc((PILLARS[n]||{}).short||'P'+n)}</button>`).join('')}</div>
  ${(N.searches||[]).filter(x=>!f||x.pillar===f).map(x=>`<a class="linkrow" href="${esc(x.url)}" target="_blank" rel="noopener"><span><span class="dot p${x.pillar}" style="margin-right:6px"></span>${esc(x.label)}</span><span class="r">Search &rsaquo;</span></a>`).join('')}`;
  root.appendChild(head);
  head.querySelectorAll('[data-f]').forEach(b=>b.onclick=()=>{state.newsFilter=Number(b.dataset.f);renderNews();});
  const src=el('div','card');src.style.marginTop='10px';
  src.innerHTML=`<h3>Sources worth a weekly look</h3>`+(N.sources||[]).map(x=>`<a class="linkrow" href="${esc(x.url)}" target="_blank" rel="noopener"><span>${esc(x.label)}<div class="n">${esc(x.note||'')}</div></span><span class="r">Open &rsaquo;</span></a>`).join('');
  root.appendChild(src);
  const mo=el('div','card');mo.style.marginTop='10px';
  const today=todayISO();
  mo.innerHTML=`<h3>Dated moments, next 6</h3>`+MOMENTS().filter(m=>m.date>=today).slice(0,6).map(m=>`<div class="linkrow" style="cursor:default"><span><span class="num" style="color:var(--muted);font-weight:600">${fmtDM(m.date)}</span> &middot; ${esc(m.event)}${m.confirmed?'':' <span class="tag">unconfirmed</span>'}<div class="n">${esc(m.use||'')}</div></span></div>`).join('');
  root.appendChild(mo);
  const bank=el('div','card');bank.style.marginTop='10px';
  const items=newsBank().slice().sort((a,b)=>(b.added||'')<(a.added||'')?-1:1);
  bank.innerHTML=`<h3>News bank</h3><div class="small">Stories worth a slot. Saved on this phone and included in the Sunday export, so the review sees what caught your eye.</div>
  <div class="field"><label for="nbTitle">Headline or the number</label><input id="nbTitle" placeholder="Sydney clearance 57.8%, a year ago 77.1%"></div>
  <div class="fgrid"><div class="field"><label for="nbUrl">Link</label><input id="nbUrl" placeholder="https://"></div><div class="field"><label for="nbPillar">Pillar</label><select id="nbPillar">${S.pillars.map(p=>`<option value="${p.n}">${p.n} &middot; ${esc(p.short)}</option>`).join('')}</select></div></div>
  <div class="field"><label for="nbAngle">The angle underneath (why one person cares this week)</label><textarea id="nbAngle" rows="2"></textarea></div>
  <div class="actions" style="justify-content:flex-start;margin-top:8px"><button class="btn primary" id="nbAdd">Bank it</button></div>
  <div style="margin-top:10px">${items.length?items.map(it=>`<div class="newsitem"><div class="t">${esc(it.title)}</div><div class="m">${pillarChip(it.pillar)} <span class="small num">${it.added?fmtDM(it.added.slice(0,10)):''}</span>${it.used?' <span class="chip POSTED">used</span>':''}</div>${it.angle?`<div class="m">${esc(it.angle)}</div>`:''}<div class="btnrow" style="margin-top:6px">${it.url?`<a class="btn small" href="${esc(it.url)}" target="_blank" rel="noopener" style="text-decoration:none">Open</a>`:''}<button class="btn small primary" data-promote="${esc(it.id)}">Make it a topical slot</button><button class="btn small" data-del="${esc(it.id)}">Remove</button></div></div>`).join(''):'<div class="empty">Nothing banked yet. When a story stops you, put it here.</div>'}</div>`;
  root.appendChild(bank);
  bank.querySelector('#nbAdd').onclick=()=>{const t=bank.querySelector('#nbTitle').value.trim();if(!t){toast('Give it a headline');return;}const it={id:'n'+Date.now().toString(36),title:t,url:bank.querySelector('#nbUrl').value.trim(),pillar:Number(bank.querySelector('#nbPillar').value),angle:bank.querySelector('#nbAngle').value.trim(),added:new Date().toISOString(),used:false};state.news=newsBank().concat([it]);renderNews();persist();toast('Banked');};
  bank.querySelectorAll('[data-del]').forEach(b=>b.onclick=()=>{state.news=newsBank().filter(x=>x.id!==b.dataset.del);renderNews();persist();});
  bank.querySelectorAll('[data-promote]').forEach(b=>b.onclick=()=>{const it=newsBank().find(x=>x.id===b.dataset.promote);if(!it)return;const w=weekFor(todayISO());const n=Object.values(state.slots).filter(s=>s.date>=w.start&&s.date<=w.end).length+1;openSheet(null,{id:`${w.id}-T${String(n).padStart(2,'0')}`,title:it.title.slice(0,80),hook:it.title,pillar:it.pillar,kind:'TOPICAL',angle:it.angle||'',notes:it.url?'Source: '+it.url:'',cta:''});it.used=true;persist();});
}
function setInsights(v){state.insightsView=v;document.querySelectorAll('#insSeg button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.v===v));document.getElementById('tab-pillars').hidden=v!=='pillars';document.getElementById('tab-hooks').hidden=v!=='hooks';}
document.querryAllPlaceholder=null;
document.querySelectorAll('#insSeg button').forEach(b=>b.onclick=()=>setInsights(b.dataset.v));

// ---------- header ----------"""
s = swap(s, "// ---------- header ----------", render, 'news render')
s = s.replace("document.querryAllPlaceholder=null;\n", "")

# ---- openSheet: accept prefill ----
s = swap(s, "function openSheet(id){\n  const s=id?state.slots[id]:{id:'',date:todayISO(),time:'06:45',format:'Reel',lane:'A',pillar:1,title:'',hook:'',angle:'',kind:'EVERGREEN',cta:'',status:'PLANNED',metrics:{}};",
"function openSheet(id,pre){\n  const s=id?state.slots[id]:{id:'',date:todayISO(),time:'06:45',format:'Reel',lane:'A',pillar:1,title:'',hook:'',angle:'',kind:'EVERGREEN',cta:'',status:'PLANNED',metrics:{},...(pre||{})};", 'openSheet sig')
s = swap(s, '<div class="field"><label for="nId">ID</label><input id="nId" placeholder="W5-01"></div>', '<div class="field"><label for="nId">ID</label><input id="nId" placeholder="W3-01" value="${esc(s.id||\'\')}"></div>', 'nId')
s = swap(s, '<select id="nPillar">${S.pillars.map(p=>`<option value="${p.n}">${p.n} &middot; ${esc(p.short)}</option>`).join(\'\')}</select>', '<select id="nPillar">${S.pillars.map(p=>`<option value="${p.n}" ${Number(s.pillar)===p.n?\'selected\':\'\'}>${p.n} &middot; ${esc(p.short)}</option>`).join(\'\')}</select>', 'nPillar')
s = swap(s, '<select id="nKind"><option>EVERGREEN</option><option>TOPICAL</option></select>', '<select id="nKind"><option ${s.kind===\'EVERGREEN\'?\'selected\':\'\'}>EVERGREEN</option><option ${s.kind===\'TOPICAL\'?\'selected\':\'\'}>TOPICAL</option></select>', 'nKind')
s = swap(s, '<div class="field"><label for="nTitle">Title</label><input id="nTitle"></div><div class="field"><label for="nHook">Hook</label><textarea id="nHook" rows="2"></textarea></div><div class="field"><label for="nCta">CTA</label><input id="nCta"></div>',
           '<div class="field"><label for="nTitle">Title</label><input id="nTitle" value="${esc(s.title||\'\')}"></div><div class="field"><label for="nHook">Hook</label><textarea id="nHook" rows="2">${esc(s.hook||\'\')}</textarea></div><div class="field"><label for="nAngle">Angle</label><textarea id="nAngle" rows="2">${esc(s.angle||\'\')}</textarea></div><div class="field"><label for="nCta">CTA</label><input id="nCta" value="${esc(s.cta||\'\')}"></div>', 'new fields')
s = swap(s, "doc.cta=q('#nCta').value.trim();doc.angle='';doc.type='';", "doc.cta=q('#nCta').value.trim();doc.angle=q('#nAngle').value.trim();doc.type='';", 'angle save')

# ---- tabs ----
s = swap(s, "['week','log','growth','pillars','hooks','scripts'].forEach(k=>document.getElementById('tab-'+k).hidden=(k!==t));",
           "['week','log','growth','insights','news','scripts'].forEach(k=>document.getElementById('tab-'+k).hidden=(k!==t));", 'tabs list')
s = swap(s, "function renderAll(){renderHeader();renderWeek();renderLog();renderGrowth();renderPillars();renderHooks();renderScripts();}",
           "function renderAll(){renderHeader();renderWeek();renderLog();renderGrowth();renderPillars();renderHooks();renderScripts();renderNews();}", 'renderAll')
s = swap(s, "try{const t=localStorage.getItem('r10k-tab');if(t)showTab(t);}catch(e){}",
           "try{const t=localStorage.getItem('r10k-tab');if(t&&['week','log','growth','insights','news','scripts'].includes(t))showTab(t);}catch(e){}", 'restore tab')

assert "—" not in s
open(p, 'w', encoding='utf-8').write(s)
print('news tab added')
