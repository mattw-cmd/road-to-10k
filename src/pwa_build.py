"""Turn template.html + plan.json into a standalone, installable PWA in ./pwa/.
Data is stored on the device (IndexedDB, localStorage fallback). Export/Import JSON for the Sunday loop.
Run: python pwa_build.py
"""
import json, os, io, sys, re
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..")) if os.path.basename(HERE)=="src" else os.path.join(HERE, "pwa")
os.makedirs(os.path.join(OUT, "icons"), exist_ok=True)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

plan = json.load(open(os.path.join(HERE, "plan.json"), encoding="utf-8"))
# same text patches as build.py
for s in plan["slots"]:
    if s["id"] == "W4-02":
        s["angle"] = s["angle"].replace("Three rises this year did more", "This year's rate rises did more")
    if s["id"] == "W2-06":
        s["angle"] = s["angle"].replace(
            "In 2024 the forward guidance said no rises until 2024 and the cash rate went up 13 times before that. Borrowers remember.",
            "In 2021 the RBA said no rise until 2024. The first came in May 2022 and twelve more followed. Borrowers remember.")

tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()

def swap(src, old, new, label):
    assert old in src, "anchor not found: " + label
    return src.replace(old, new, 1)

# ---- head / document wrapper ----
head = """<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#000814">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Road to 10k">
<meta name="description" content="Instagram content calendar, post log and growth tracker for @mattwade_____. Data stays on this device.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
"""
tpl = head + tpl
tpl = swap(tpl, "<style>\n:root{", "<style>\nhtml{color-scheme:dark;background:#000814}\n:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}\n:root{", "style open")
tpl = swap(tpl, "</style>\n\n<header class=\"top\">", "</style>\n</head>\n<body>\n<header class=\"top\">", "body open")
tpl = tpl.rstrip() + "\n</body>\n</html>\n"

# ---- header: data button ----
tpl = swap(tpl,
    '<div class="streak zero" id="streak" title="Consecutive weeks hitting 8 posts">',
    '<div style="display:flex;align-items:center;gap:8px"><button class="btn small" id="dataBtn" aria-label="Backup and sync" title="Backup and sync">Sync</button>\n    <div class="streak zero" id="streak" title="Consecutive weeks hitting 8 posts">',
    "streak header")
tpl = swap(tpl,
    '<span id="streakL">week streak</span>\n    </div>\n  </div>\n</header>',
    '<span id="streakL">week streak</span>\n    </div></div>\n  </div>\n</header>',
    "header close")

# ---- persistence: replace the artifact db layer with device storage ----
start = tpl.index("// ---------- persistence ----------")
end = tpl.index("// ---------- tabs ----------")
persistence = r"""// ---------- persistence (on this device) ----------
let toastT=null;
function toast(msg){let t=document.querySelector('.toast');if(!t){t=el('div','toast');document.body.appendChild(t);}t.textContent=msg;clearTimeout(toastT);toastT=setTimeout(()=>t.remove(),2600);}
const KEY='road-to-10k-state-v1';
function idb(){return new Promise((res,rej)=>{try{const r=indexedDB.open('road-to-10k',1);r.onupgradeneeded=()=>r.result.createObjectStore('kv');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error);}catch(e){rej(e);}});}
async function idbGet(k){try{const d=await idb();return await new Promise((res,rej)=>{const t=d.transaction('kv','readonly').objectStore('kv').get(k);t.onsuccess=()=>res(t.result);t.onerror=()=>rej(t.error);});}catch(e){return undefined;}}
async function idbSet(k,v){try{const d=await idb();await new Promise((res,rej)=>{const t=d.transaction('kv','readwrite');t.objectStore('kv').put(v,k);t.oncomplete=res;t.onerror=()=>rej(t.error);});return true;}catch(e){return false;}}
function snapshot(forExport){return {version:1,app:'road-to-10k',exportedAt:new Date().toISOString(),handle:S.handle,slots:state.slots,growth:state.growth,reviews:state.reviews,meta:state.meta,news:state.news||[],bank:forExport?undefined:(state.bank||[])};}
let persistT=null;
function persist(){clearTimeout(persistT);persistT=setTimeout(async()=>{const snap=snapshot();const ok=await idbSet(KEY,snap);try{localStorage.setItem(KEY,JSON.stringify(snap));}catch(e){}state.dbState=ok?'on':'off';renderHeader();},150);}
function applySnapshot(snap,mode){
  if(!snap||typeof snap!=='object')return 0;let n=0;
  if(snap.slots&&typeof snap.slots==='object'){const arr=Array.isArray(snap.slots)?snap.slots:Object.values(snap.slots);arr.forEach(d=>{if(!d||!d.id)return;if(mode==='replace'){state.slots[d.id]=d;}else{state.slots[d.id]={...(state.slots[d.id]||{}),...d};}n++;});}
  if(Array.isArray(snap.growth)){const byDate={};state.growth.forEach(r=>byDate[r.date]=r);snap.growth.forEach(r=>{if(r&&r.date&&r.count!=null)byDate[r.date]=r;});state.growth=Object.values(byDate).sort((a,b)=>a.date<b.date?-1:1);}
  if(snap.reviews&&typeof snap.reviews==='object'){state.reviews={...state.reviews,...snap.reviews};}
  if(snap.meta&&typeof snap.meta==='object'){const m=snap.meta;state.meta={...state.meta,...m,stories:{...(state.meta.stories||{}),...(m.stories||{})}};if(Array.isArray(m.weeks)&&m.weeks.length)state.meta.weeks=m.weeks;if(Array.isArray(m.moments)&&m.moments.length)state.meta.moments=m.moments;}
  if(snap.stories&&typeof snap.stories==='object'){state.meta.stories={...(state.meta.stories||{}),...snap.stories};}
  if(Array.isArray(snap.weeks)&&snap.weeks.length)state.meta.weeks=snap.weeks;
  if(Array.isArray(snap.news)){const by={};(state.news||[]).forEach(x=>by[x.id]=x);snap.news.forEach(x=>{if(x&&x.id)by[x.id]={...(by[x.id]||{}),...x};});state.news=Object.values(by);}
  if(Array.isArray(snap.bank)){mergeBank(snap.bank);}
  return n;
}
function mergeBank(items){const by={};(state.bank||[]).forEach(x=>by[x.id]=x);items.forEach(x=>{if(!x||!x.id)return;const prev=by[x.id]||{};const used=Array.from(new Set([...(prev.used||[]),...(x.used||[])])).sort();by[x.id]={...prev,...x,used};});state.bank=Object.values(by);}
function backfillSlots(){const gk={};(S.groups||[]).forEach(g=>gk[g.pillar]=g.key);Object.values(state.slots).forEach(s=>{if(!s.group&&gk[s.pillar])s.group=gk[s.pillar];if(s.bankId===undefined)s.bankId=null;if(!Array.isArray(s.swapHistory))s.swapHistory=[];});}
async function saveSlot(doc){state.slots[doc.id]=doc;renderAll();persist();toast('Saved on this phone');}
async function saveGrowth(list){state.growth=list;renderAll();persist();toast('Reading saved');}
async function connect(){
  let snap=await idbGet(KEY);
  if(!snap){try{const raw=localStorage.getItem(KEY);if(raw)snap=JSON.parse(raw);}catch(e){}}
  if(snap){applySnapshot(snap,'replace');state.dbState='on';}else{state.dbState='on';persist();}
  // built-in plan sits underneath stored data: new fields shipped with the app (scripts, angles) show up without losing statuses or numbers
  PLAN.slots.forEach(ps=>{const st=state.slots[ps.id]||{};state.slots[ps.id]={...ps,...st,script:(st.script&&(st.script.spoken||st.script.slides))?st.script:ps.script};});
  (S.retiredSlots||[]).forEach(id=>{const st=state.slots[id];if(st&&(st.status||'PLANNED')==='PLANNED'&&!st.updatedAt&&!(st.metrics&&Object.keys(st.metrics).length))delete state.slots[id];});
  // built-in bank underneath the stored bank: stored `used` dates survive, new items ship with the app
  {const stored=state.bank||[];state.bank=[];mergeBank(PLAN.bank||[]);mergeBank(stored);}
  backfillSlots();
  renderAll();
}
function fileName(){return 'road-to-10k-export-'+todayISO()+'.json';}
async function exportData(){
  const text=JSON.stringify(snapshot(true),null,1);
  const blob=new Blob([text],{type:'application/json'});
  const file=new File([blob],fileName(),{type:'application/json'});
  try{if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],title:'Road to 10k export'});state.meta.lastExport=todayISO();persist();toast('Shared');return;}}catch(e){if(e&&e.name==='AbortError')return;}
  try{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=fileName();document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},1000);state.meta.lastExport=todayISO();persist();toast('Downloaded');return;}catch(e){}
  try{await navigator.clipboard.writeText(text);toast('Copied to clipboard');}catch(e){toast('Export failed');}
}
function importText(text){
  let snap;try{snap=JSON.parse(text);}catch(e){toast('That is not a valid JSON file');return;}
  if(snap.app&&snap.app!=='road-to-10k'){toast('Not a Road to 10k file');return;}
  const n=applySnapshot(snap,'merge');state.meta.lastImport=todayISO();renderAll();persist();toast(`Imported ${n} slot${n===1?'':'s'}`);
}
function openDataSheet(){
  closeSheet();
  const g=state.growth.length;const n=Object.keys(state.slots).length;
  sheetEl=el('div','sheet-bg');
  sheetEl.innerHTML=`<div class="sheet" role="dialog" aria-modal="true" aria-label="Backup and sync">
  <h3>Backup and sync</h3><div class="sub">Everything lives on this phone. ${n} slots, ${g} follower readings, ${Object.keys(state.reviews).length} reviews, ${(state.bank||[]).length} bank items (the bank stays on the phone and is not exported).${state.meta.lastExport?' Last export '+fmtDM(state.meta.lastExport)+'.':''}${state.meta.lastImport?' Last import '+fmtDM(state.meta.lastImport)+'.':''}</div>
  <h2>Export</h2><div class="small">Sunday: share the file into Google Drive, Mortgage Content Machine / Instagram / sync. The weekly review reads it from there.</div>
  <div class="actions" style="justify-content:flex-start;margin-top:8px"><button class="btn primary" id="exBtn">Export data</button><button class="btn" id="copyBtn">Copy as text</button></div>
  <h2>Import</h2><div class="small">Monday: open the import file the review left in the same sync folder, or paste its contents.</div>
  <div class="field"><label for="impFile">Choose file</label><input id="impFile" type="file" accept="application/json,.json"></div>
  <div class="field"><label for="impText">Or paste JSON</label><textarea id="impText" rows="3" placeholder="{ ... }"></textarea></div>
  <div class="actions" style="justify-content:flex-start;margin-top:8px"><button class="btn primary" id="impBtn">Import pasted text</button></div>
  <h2>Danger zone</h2><div class="actions" style="justify-content:flex-start"><button class="btn" id="resetBtn" style="color:var(--bad);border-color:var(--bad)">Reset to the launch plan</button></div>
  <div class="actions"><button class="btn" id="dsClose">Close</button></div></div>`;
  document.body.appendChild(sheetEl);
  sheetEl.addEventListener('click',e=>{if(e.target===sheetEl)closeSheet();});
  sheetEl.querySelector('#dsClose').onclick=closeSheet;
  sheetEl.querySelector('#exBtn').onclick=exportData;
  sheetEl.querySelector('#copyBtn').onclick=async()=>{try{await navigator.clipboard.writeText(JSON.stringify(snapshot(true)));toast('Copied');}catch(e){toast('Copy failed');}};
  sheetEl.querySelector('#impFile').onchange=e=>{const f=e.target.files&&e.target.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{importText(String(r.result));closeSheet();};r.readAsText(f);};
  sheetEl.querySelector('#impBtn').onclick=()=>{const t=sheetEl.querySelector('#impText').value.trim();if(!t){toast('Nothing to import');return;}importText(t);closeSheet();};
  sheetEl.querySelector('#resetBtn').onclick=()=>{if(!confirm('Replace everything on this phone with the launch plan? Export first if you want to keep your numbers.'))return;state.slots={};PLAN.slots.forEach(s=>state.slots[s.id]={...s,status:'PLANNED',metrics:{}});state.growth=PLAN.growth.slice();state.reviews={};state.meta={};state.news=[];state.bank=[];mergeBank(PLAN.bank||[]);backfillSlots();renderAll();persist();closeSheet();toast('Reset');};
}
document.getElementById('dataBtn').onclick=openDataSheet;

"""
tpl = tpl[:start] + persistence + tpl[end:]

# header connection chip wording
tpl = swap(tpl,
    "c.querySelector('span').textContent=state.dbState==='on'?'saved live':state.dbState==='off'?'not saving':'connecting';",
    "c.querySelector('span').textContent=state.dbState==='on'?'saved on this phone':state.dbState==='off'?'storage blocked, export often':'loading';",
    "conn wording")
tpl = swap(tpl, "state.dbState==='on'?'on':state.dbState==='off'?'off':''", "state.dbState==='on'?'on':state.dbState==='off'?'off':''", "conn class")

# service worker registration + stale-state guard
tpl = swap(tpl, "connect();\n})();", "connect();\nif('serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('sw.js').catch(()=>{});});}\n})();", "sw register")

# no claude references left
assert "claude.use" not in tpl and "window.claude" not in tpl, "claude runtime reference left in PWA"
# no em dashes
assert "\u2014" not in tpl

plan_js = json.dumps(plan, ensure_ascii=False).replace("</", "<\\/")
html = tpl.replace("/*__PLAN__*/", plan_js)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)
print("index.html", len(html), "bytes")

# ---- manifest ----
manifest = {
  "name": "Road to 10k", "short_name": "Road to 10k",
  "description": "Instagram content calendar, post log and growth tracker for @mattwade_____.",
  "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
  "background_color": "#000814", "theme_color": "#1c6cff",
  "icons": [
    {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
json.dump(manifest, open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf-8"), indent=1)

# ---- service worker: cache the shell, network-first for index so updates land ----
sw = """const CACHE='road-to-10k-v%s';
const SHELL=['./','./index.html','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png','./icons/apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const req=e.request; if(req.method!=='GET') return;
  const url=new URL(req.url);
  if(url.origin!==location.origin){ e.respondWith(fetch(req).catch(()=>caches.match(req))); return; }
  if(req.mode==='navigate'||url.pathname.endsWith('index.html')||url.pathname.endsWith('/')){
    e.respondWith(fetch(req).then(r=>{const cp=r.clone();caches.open(CACHE).then(c=>c.put(req,cp));return r;}).catch(()=>caches.match(req).then(r=>r||caches.match('./index.html'))));
    return;
  }
  e.respondWith(caches.match(req).then(r=>r||fetch(req).then(res=>{const cp=res.clone();caches.open(CACHE).then(c=>c.put(req,cp));return res;})));
});
""" % __import__("datetime").datetime.now().strftime("%Y%m%d%H%M")
open(os.path.join(OUT, "sw.js"), "w", encoding="utf-8").write(sw)

# ---- icons ----
def font(size):
    for f in [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
        if os.path.exists(f): return ImageFont.truetype(f, size)
    return ImageFont.load_default()
def icon(size, maskable=False, path=None):
    im = Image.new("RGB", (size, size), "#000814")
    d = ImageDraw.Draw(im)
    pad = size * (0.2 if maskable else 0.12)
    # upward line as the mark
    pts = [(pad, size - pad), (size * 0.42, size * 0.62), (size * 0.58, size * 0.72), (size - pad, pad * 1.35)]
    d.line(pts, fill="#1c6cff", width=max(4, size // 18), joint="curve")
    r = size // 22
    d.ellipse([size - pad - r, pad * 1.35 - r, size - pad + r, pad * 1.35 + r], fill="#FFFFFF")
    f = font(int(size * 0.26))
    txt = "10k"
    bb = d.textbbox((0, 0), txt, font=f)
    d.text((pad, pad * 0.75), txt, font=f, fill="#FFFFFF")
    im.save(path, "PNG")
icon(192, path=os.path.join(OUT, "icons", "icon-192.png"))
icon(512, path=os.path.join(OUT, "icons", "icon-512.png"))
icon(512, maskable=True, path=os.path.join(OUT, "icons", "icon-512-maskable.png"))
icon(180, path=os.path.join(OUT, "icons", "apple-touch-icon.png"))

open(os.path.join(OUT, ".nojekyll"), "w").write("")
open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(
"""# Road to 10k

Installable web app for Matt Wade's Instagram content system (@mattwade_____): calendar, post log, growth chart, pillar and hook performance, streak.

- All data is stored on the device (IndexedDB). Nothing is sent anywhere.
- **Sync** in the header exports a JSON snapshot and imports one back. The Sunday review reads the export from Google Drive and leaves an import file in the same folder.
- Built from `plan.json` + `template.html` with `pwa_build.py` in the PROJECT AUTOMATE session scratchpad.

Install: open the site on your phone, Share, Add to Home Screen.
""")
print("pwa written to", OUT)
