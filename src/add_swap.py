"""Slot swap from the script bank (spec: SCRIPT BANK + SWAP SPEC.md, 17 Sep 2026). Idempotent on template.html."""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = 'template.html'
s = open(p, encoding='utf-8').read()
if 'openSwapSheet' in s:
    print('swap already present'); sys.exit(0)

def swap(src, old, new, label):
    assert old in src, 'anchor not found: ' + label
    return src.replace(old, new, 1)

# state
s = swap(s, "insightsView:'pillars', news:[], newsFilter:0 };", "insightsView:'pillars', news:[], newsFilter:0, bank:[] };", 'state')

# CSS
s = swap(s, ".small{font-size:12.5px;color:var(--muted)}",
""".small{font-size:12.5px;color:var(--muted)}
.swaprow{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:start;padding:12px 0;border-top:1px solid var(--line)}
.swaprow:first-child{border-top:0}
.swaprow.cool{opacity:.55}
.swaprow .t{font-weight:500;font-size:15px;letter-spacing:-.01em}
.swaprow .h{font-size:13.5px;color:var(--ink2);margin-top:3px;font-weight:300}
.swaprow .m{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;align-items:center}
.warn{background:rgba(255,136,51,.14);color:var(--color-tag-tangerine);border-radius:12px;padding:8px 10px;font-size:12.5px;margin-top:6px}
.current{background:var(--surface2);border-radius:16px;padding:10px 12px;margin-top:8px;font-size:13px}""", 'css')

# slot rows: Swap control (absent on POSTED, only when the slot has a group)
s = swap(s, "${s.status==='POSTED'?scoreBadge(sc[s.id]):''}</div>`;\n    list.appendChild(row);",
           "${s.status==='POSTED'?scoreBadge(sc[s.id]):''}${s.status!=='POSTED'&&s.group?`<button class=\"btn small\" data-swap=\"${esc(s.id)}\">Swap</button>`:''}</div>`;\n    list.appendChild(row);", 'slot swap button')
# today card: Swap next to Open script
s = swap(s, "${s.script?`<button class=\"btn small\" data-script=\"${esc(s.id)}\">Open script</button>`:''}</div>",
           "${s.script?`<button class=\"btn small\" data-script=\"${esc(s.id)}\">Open script</button>`:''}${s.status!=='POSTED'&&s.group?`<button class=\"btn small\" data-swap=\"${esc(s.id)}\">Swap</button>`:''}</div>", 'today swap button')
# handlers in renderWeek
s = swap(s, "  root.querySelectorAll('[data-script]').forEach(b=>b.onclick=()=>{showTab('scripts');const t=document.getElementById('script-'+b.dataset.script);if(t)t.scrollIntoView({block:'start'});});\n}",
           "  root.querySelectorAll('[data-script]').forEach(b=>b.onclick=()=>{showTab('scripts');const t=document.getElementById('script-'+b.dataset.script);if(t)t.scrollIntoView({block:'start'});});\n  root.querySelectorAll('[data-swap]').forEach(b=>b.onclick=()=>openSwapSheet(b.dataset.swap));\n}", 'week handlers')

# Scripts tab: date order, renders from slots
s = swap(s, "const withScript=slots.filter(s=>s.script&&(s.script.spoken||s.script.slides)).sort((a,b)=>(a.script.order||99)-(b.script.order||99)||(a.date<b.date?-1:1));",
           "const withScript=slots.filter(s=>s.script&&(s.script.spoken||s.script.slides)).sort((a,b)=>(a.date+a.time)<(b.date+b.time)?-1:1);", 'scripts sort')
s = swap(s, "In filming order: Lane A at the desk first, then Lane B, then carousels to build. New scripts arrive with each Sunday import.",
           "In date order, rendered from the same slots as This week, so a swap shows here at once. Film the Lane A reels first, then Lane B, then build the carousels. ${(state.bank||[]).length} scripts in the bank.", 'scripts header')
s = swap(s, "<span class=\"tag num\">${sc.order?sc.order+'.':''} ${esc(s.id)}</span>", "<span class=\"tag num\">${esc(s.id)}</span>${s.bankId?`<span class=\"tag\">from bank ${esc(s.bankId)}</span>`:''}", 'scripts id tag')

# swap logic + sheet, inserted before header render
logic = r"""// ---------- SWAP (script bank) ----------
const SWAP_FIELDS=['type','title','hook','angle','cta','kind','disclaimer','onScreen','script','filmWindow'];
function bankById(id){return (state.bank||[]).find(b=>b.id===id);}
function daysBetween(a,b){return Math.round((parse(b)-parse(a))/DAY);}
function lastUsed(item){return (item.used||[]).slice().sort().pop()||null;}
function swapCandidates(slot){
  const today=todayISO();const cool=S.swapCooldownDays||28;
  const usedThisWeek=new Set(Object.values(state.slots).filter(x=>x.id!==slot.id&&x.week===slot.week&&x.bankId).map(x=>x.bankId));
  return (state.bank||[]).filter(b=>b.group===slot.group&&b.format===slot.format&&b.id!==slot.bankId)
    .filter(b=>!(b.kind==='TOPICAL'&&b.expires&&b.expires<today))
    .filter(b=>!usedThisWeek.has(b.id))
    .map(b=>{const lu=lastUsed(b);return {...b,_lastUsed:lu,_cool:!!(lu&&daysBetween(lu,today)<cool)};})
    .sort((a,b)=>(a._cool===b._cool?0:a._cool?1:-1)||(a.kind===b.kind?0:a.kind==='TOPICAL'?-1:1)||a.title.localeCompare(b.title));
}
function applySwap(slotId,bankId){
  const slot=state.slots[slotId];const item=bankById(bankId);if(!slot||!item)return;
  const today=todayISO();
  const content={};SWAP_FIELDS.forEach(k=>content[k]=slot[k]);content.notes=slot.notes||'';
  slot.swapHistory=Array.isArray(slot.swapHistory)?slot.swapHistory:[];
  slot.swapHistory.push({at:today,fromBankId:slot.bankId||null,toBankId:bankId,content});
  SWAP_FIELDS.forEach(k=>{if(item[k]!==undefined)slot[k]=item[k];else if(k==='script')slot.script=item.script;});
  slot.script=item.script?JSON.parse(JSON.stringify(item.script)):slot.script;
  if(item.confirm){const line='CONFIRM before posting: '+item.confirm;slot.notes=(slot.notes?slot.notes+'\n':'')+line;}
  slot.bankId=bankId;slot.updatedAt=new Date().toISOString();
  item.used=Array.from(new Set([...(item.used||[]),today])).sort();
  renderAll();persist();toast('Swapped in: '+item.title);
}
function undoSwap(slotId){
  const slot=state.slots[slotId];if(!slot||!Array.isArray(slot.swapHistory)||!slot.swapHistory.length)return;
  const h=slot.swapHistory.pop();
  const item=bankById(h.toBankId||slot.bankId);if(item)item.used=(item.used||[]).filter(d=>d!==h.at);
  SWAP_FIELDS.forEach(k=>{slot[k]=h.content[k];});slot.notes=h.content.notes||'';
  slot.bankId=h.fromBankId||null;slot.updatedAt=new Date().toISOString();
  renderAll();persist();toast('Swap undone');
}
function openSwapSheet(slotId){
  const slot=state.slots[slotId];if(!slot)return;if(slot.status==='POSTED')return;
  closeSheet();
  const g=(S.groups||[]).find(x=>x.key===slot.group);
  const cands=swapCandidates(slot);
  sheetEl=el('div','sheet-bg');
  sheetEl.innerHTML=`<div class="sheet" role="dialog" aria-modal="true" aria-label="Swap this slot">
  <h3>Swap ${esc(slot.format.toLowerCase())}</h3><div class="sub">${esc(slot.id)} &middot; ${fmtShort(slot.date)} ${esc(slot.time)} &middot; ${esc(g?g.label:slot.group||'')} &middot; ${pillarChip(slot.pillar,true)}</div>
  <div class="current"><div class="small">Currently in the slot</div><div style="font-weight:500">${esc(slot.title)}</div><div class="small" style="color:var(--ink2)">${esc(slot.hook)}</div>${slot.bankId?`<div class="small">from bank ${esc(slot.bankId)}</div>`:''}${slot.status==='FILMED'&&slot.format==='Reel'?'<div class="warn">This reel is already filmed. Swapping means filming the new script.</div>':''}</div>
  ${Array.isArray(slot.swapHistory)&&slot.swapHistory.length?`<div class="actions" style="justify-content:flex-start;margin-top:8px"><button class="btn small" id="undoSwap">Undo last swap (${fmtDM(slot.swapHistory[slot.swapHistory.length-1].at)})</button></div>`:''}
  <h2>${cands.length} ${esc(slot.format.toLowerCase())}${cands.length===1?'':'s'} in this group</h2>
  ${cands.length?cands.map(b=>`<div class="swaprow ${b._cool?'cool':''}"><div><div class="t">${esc(b.title)}</div><div class="h">${esc(b.hook)}</div><div class="m"><span class="chip ${esc(b.kind)}">${esc(b.kind)}</span>${b.lane&&b.lane!=='-'?`<span class="tag">Lane ${esc(b.lane)}</span>`:''}${b.script&&b.script.words?`<span class="tag num">${b.script.words} words</span>`:''}${b.expires?`<span class="tag num">expires ${fmtDM(b.expires)}</span>`:''}${b._lastUsed?`<span class="tag num">last used ${fmtDM(b._lastUsed)}</span>`:''}</div>${b.confirm?`<div class="warn">Confirm before posting: ${esc(b.confirm)}</div>`:''}</div><button class="btn small primary" data-choose="${esc(b.id)}">Choose</button></div>`).join(''):'<div class="empty">Nothing in the bank fits this slot right now. The Sunday import refills it.</div>'}
  <div class="actions"><button class="btn" id="swClose">Close</button></div></div>`;
  document.body.appendChild(sheetEl);
  sheetEl.addEventListener('click',e=>{if(e.target===sheetEl)closeSheet();});
  sheetEl.querySelector('#swClose').onclick=closeSheet;
  const u=sheetEl.querySelector('#undoSwap');if(u)u.onclick=()=>{undoSwap(slotId);closeSheet();};
  sheetEl.querySelectorAll('[data-choose]').forEach(b=>b.onclick=()=>{
    if(slot.status==='FILMED'&&slot.format==='Reel'&&!confirm('This reel is already filmed. Swap the script anyway?'))return;
    applySwap(slotId,b.dataset.choose);closeSheet();
  });
}

// ---------- header ----------"""
s = swap(s, "// ---------- header ----------", logic, 'swap logic')

assert "—" not in s
open(p, 'w', encoding='utf-8').write(s)
print('swap added')
