"""Restyle template.html to the Copilot Money reference: midnight canvas, thin body type, display headings,
one signal blue, candy pillar tags at jaunty angles, inset-lit surfaces. Idempotent."""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = 'template.html'
s = open(p, encoding='utf-8').read()
if '--color-midnight-canvas' in s:
    print('already restyled'); sys.exit(0)

def swap(src, old, new, label, count=1):
    assert old in src, 'anchor not found: ' + label
    return src.replace(old, new, count)

# ---- fonts ----
s = swap(s, '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap">',
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=Space+Grotesk:wght@500;600;700&display=swap">', 'fonts')

# ---- tokens: one committed dark theme ----
start = s.index('<style>\n:root{')
end = s.index('*{box-sizing:border-box}')
tokens = """<style>
:root{
  /* Copilot Money reference tokens */
  --color-midnight-canvas:#000814; --color-deep-surface:#010d1e; --color-indigo-surface:#001533; --color-cobalt-surface:#00215e;
  --color-paper-white:#ffffff; --color-fog:#ccced0; --color-mist:#999ca1; --color-steel-border:#11263b; --color-signal-blue:#1c6cff;
  --color-tag-coral:#ff4433; --color-tag-lime:#00cc4b; --color-tag-tangerine:#ff8833; --color-tag-hot-pink:#ff33aa; --color-tag-violet:#9019e6;
  --color-tag-sunflower:#ffcc02; --color-tag-sky:#00acfe; --color-tag-ember:#ea687c; --color-tag-olive:#94ae43; --color-tag-slate:#5c6f8a;
  /* app roles */
  --bg:var(--color-midnight-canvas); --surface:var(--color-deep-surface); --surface2:var(--color-indigo-surface); --surface3:var(--color-cobalt-surface);
  --line:var(--color-steel-border);
  --ink:var(--color-paper-white); --ink2:var(--color-fog); --muted:var(--color-mist);
  --accent:var(--color-signal-blue); --accent-ink:#ffffff; --accent-soft:rgba(28,108,255,.18);
  --good:var(--color-tag-lime); --good-soft:rgba(0,204,75,.16); --warn:var(--color-tag-sunflower); --warn-soft:rgba(255,204,2,.16); --bad:var(--color-tag-coral); --bad-soft:rgba(255,68,51,.18);
  --p1:var(--color-tag-sky); --p2:var(--color-tag-sunflower); --p3:var(--color-tag-coral); --p4:var(--color-tag-violet); --p5:var(--color-tag-lime);
  --p1-ink:#000814; --p2-ink:#000814; --p3-ink:#ffffff; --p4-ink:#ffffff; --p5-ink:#000814;
  --shadow:rgba(255,255,255,.08) 4px 4px 8px 0 inset, rgba(255,255,255,.16) 4px 4px 16px -4px inset, rgba(0,0,0,.2) -4px -4px 16px -4px inset, rgba(255,255,255,.4) 1px 1px 1px -.5px inset;
  --shadow-glow:rgba(38,113,217,.08) 0 0 12px 0 inset, rgba(0,0,0,.32) 0 -4px 8px 0 inset;
  --shadow-pressed:rgba(0,0,0,.2) -4px -4px 16px -4px inset;
  --radius:24px; --radius-btn:16px; --radius-tag:20px;
  --font-display:"Space Grotesk",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --font-body:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  color-scheme:dark;
}
"""
s = s[:start] + tokens + s[end:]

# ---- base type ----
s = swap(s, "body{margin:0;background:var(--bg);color:var(--ink);font-family:Poppins,system-ui,-apple-system,\"Segoe UI\",Roboto,sans-serif;font-size:15px;line-height:1.45;-webkit-font-smoothing:antialiased}",
            "body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);font-weight:300;font-size:15px;line-height:1.45;letter-spacing:-.01em;-webkit-font-smoothing:antialiased;font-feature-settings:\"ss07\"}\nb,strong{font-weight:500}\n.display,h3,.tile .v,.streak .n,.weeknav .wk,.slot .when .n,.brand .h,.sheet h3,.prompter .bar>div>div:first-child{font-family:var(--font-display)}", 'body font')

# header
s = swap(s, ".brand .h{font-weight:700;font-size:17px;letter-spacing:-.01em}", ".brand .h{font-weight:600;font-size:20px;letter-spacing:-.02em;line-height:1}", 'brand h')
s = swap(s, ".brand .s{font-size:12px;color:var(--muted)}", ".brand .s{font-size:12px;color:var(--muted);font-weight:300}", 'brand s')
s = swap(s, ".streak{display:flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);font-size:13px;font-weight:600;white-space:nowrap}",
            ".streak{display:flex;align-items:center;gap:8px;padding:6px 12px;border-radius:9999px;background:var(--surface);border:1px solid rgba(17,38,59,.6);box-shadow:var(--shadow);font-size:12px;font-weight:300;color:var(--ink2);white-space:nowrap}", 'streak')
s = swap(s, ".streak .n{font-size:20px;font-weight:700;line-height:1}", ".streak .n{font-size:22px;font-weight:600;line-height:1;color:var(--ink)}", 'streak n')

# eyebrows and headings
s = swap(s, "h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:22px 0 10px;font-weight:600}",
            "h2{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--accent);margin:24px 0 10px;font-weight:600;line-height:1}", 'h2')
s = swap(s, "h3{font-size:16px;margin:0 0 6px;font-weight:600;text-wrap:balance}", "h3{font-size:22px;margin:0 0 6px;font-weight:500;letter-spacing:-.02em;line-height:1.1;text-wrap:balance}", 'h3')

# cards and tiles: inset light, no drop shadow
s = swap(s, ".card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:14px;box-shadow:var(--shadow)}",
            ".card{background:var(--surface);border:1px solid rgba(17,38,59,.4);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow)}", 'card')
s = swap(s, ".card + .card{margin-top:10px}", ".card + .card{margin-top:12px}", 'card gap')
s = swap(s, ".today{border-left:4px solid var(--accent)}", ".today{background:var(--surface2);box-shadow:var(--shadow),var(--shadow-glow);overflow:visible;position:relative}\n.hero-tags{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:2px 0 10px}\n.hero-tags .chip{padding:7px 14px;font-size:12px;font-weight:500;letter-spacing:.02em;text-transform:uppercase;border-radius:var(--radius-tag);box-shadow:rgba(255,255,255,.35) 1px 1px 1px -.5px inset, rgba(0,0,0,.25) -2px -2px 6px -2px inset}\n.hero-tags .chip:nth-child(1){transform:rotate(-6deg)}\n.hero-tags .chip:nth-child(2){transform:rotate(4deg)}\n.hero-tags .chip:nth-child(3){transform:rotate(-2deg)}\n.hero-tags .chip:nth-child(4){transform:rotate(5deg)}\n.hero-tags .chip:nth-child(5){transform:rotate(-3deg)}\n.tagfill.p1{background:var(--p1);color:var(--p1-ink)} .tagfill.p2{background:var(--p2);color:var(--p2-ink)} .tagfill.p3{background:var(--p3);color:var(--p3-ink)} .tagfill.p4{background:var(--p4);color:var(--p4-ink)} .tagfill.p5{background:var(--p5);color:var(--p5-ink)}\n.hero-tags .chip.fmt{background:var(--color-tag-slate);color:#fff}\n.hero-tags .chip.TOPICAL{background:var(--color-tag-tangerine);color:#000814}\n.hero-tags .chip.EVERGREEN{background:var(--color-tag-olive);color:#000814}\n.hero-tags .chip.POSTED{background:var(--good);color:#000814} .hero-tags .chip.SKIPPED{background:var(--bad);color:#fff} .hero-tags .chip.FILMED{background:var(--accent);color:#fff} .hero-tags .chip.PLANNED{background:var(--surface3);color:var(--ink2);border-color:var(--line)}\n.today h3{font-size:30px;line-height:1.05;letter-spacing:-.02em;font-weight:600}\n.today .hook{font-size:17px;font-weight:200;color:var(--ink);letter-spacing:-.01em}", 'today hero')
s = swap(s, ".tile{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:12px 14px}", ".tile{background:var(--surface);border:1px solid rgba(17,38,59,.4);border-radius:var(--radius);padding:16px 18px;box-shadow:var(--shadow)}", 'tile')
s = swap(s, ".tile .l{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}", ".tile .l{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;font-weight:600}", 'tile l')
s = swap(s, ".tile .v{font-size:26px;font-weight:700;line-height:1.1;margin-top:4px}", ".tile .v{font-size:34px;font-weight:600;line-height:1;margin-top:6px;letter-spacing:-.02em}", 'tile v')

# chips: tag radius
s = swap(s, ".chip{display:inline-flex;align-items:center;gap:6px;padding:3px 9px;border-radius:999px;font-size:11.5px;font-weight:600;letter-spacing:.02em;border:1px solid transparent;white-space:nowrap}",
            ".chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:var(--radius-tag);font-size:11.5px;font-weight:500;letter-spacing:.02em;border:1px solid transparent;white-space:nowrap}", 'chip')
s = swap(s, ".chip.PLANNED{background:transparent;border-color:var(--line);color:var(--ink2)}", ".chip.PLANNED{background:transparent;border-color:rgba(204,206,208,.35);color:var(--ink2)}", 'chip planned')
s = swap(s, ".chip.POSTED{background:var(--good-soft);color:var(--good)}", ".chip.POSTED{background:var(--good-soft);color:var(--good)} .hero-tags .chip.POSTED{color:#000814}", 'chip posted')
s = swap(s, ".chip.EVERGREEN{background:var(--surface2);color:var(--ink2)}", ".chip.EVERGREEN{background:var(--surface2);color:var(--ink2);border-color:rgba(17,38,59,.6)}", 'chip evergreen')
s = swap(s, ".chip.TOPICAL{background:var(--warn-soft);color:var(--warn)}", ".chip.TOPICAL{background:rgba(255,136,51,.16);color:var(--color-tag-tangerine)}", 'chip topical')
s = swap(s, ".chip.fmt{background:var(--surface2);color:var(--ink)}", ".chip.fmt{background:var(--surface2);color:var(--ink);border-color:rgba(17,38,59,.6)}", 'chip fmt')

# slots
s = swap(s, ".slot{display:grid;grid-template-columns:52px 1fr auto;gap:10px;align-items:start;padding:12px 0;border-top:1px solid var(--line)}", ".slot{display:grid;grid-template-columns:52px 1fr auto;gap:10px;align-items:start;padding:14px 0;border-top:1px solid rgba(17,38,59,.7)}", 'slot')
s = swap(s, ".slot .when .n{font-size:20px;font-weight:700;line-height:1}", ".slot .when .n{font-size:24px;font-weight:600;line-height:1}", 'slot n')
s = swap(s, ".slot .title{font-weight:600;font-size:15px}", ".slot .title{font-weight:500;font-size:16px;letter-spacing:-.01em}", 'slot title')
s = swap(s, ".slot .hook{font-size:13.5px;color:var(--ink2);margin-top:2px}", ".slot .hook{font-size:14px;color:var(--ink2);margin-top:3px;font-weight:300}", 'slot hook')

# buttons
s = swap(s, ".btn{border:1px solid var(--line);background:var(--surface);border-radius:10px;padding:8px 12px;font-weight:600;font-size:13px}", ".btn{border:1px solid rgba(255,255,255,.7);background:transparent;color:var(--ink);border-radius:var(--radius-btn);padding:10px 16px;font-weight:300;font-size:14px}", 'btn')
s = swap(s, ".btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}", ".btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent);font-weight:400}", 'btn primary')
s = swap(s, ".btn.small{padding:5px 9px;font-size:12px}", ".btn.small{padding:7px 12px;font-size:12.5px;border-radius:12px}", 'btn small')

# week nav, progress
s = swap(s, ".weeknav .wk{font-weight:700;font-size:16px}", ".weeknav .wk{font-weight:600;font-size:20px;letter-spacing:-.02em}", 'wk')
s = swap(s, ".progress{height:8px;border-radius:999px;background:var(--surface2);overflow:hidden;margin:8px 0 4px}", ".progress{height:8px;border-radius:9999px;background:var(--surface3);overflow:hidden;margin:10px 0 6px;box-shadow:var(--shadow-pressed)}", 'progress')
s = swap(s, ".progress i.short{background:var(--warn)}", ".progress i.short{background:var(--color-tag-tangerine)}", 'progress short')

# bottom nav
s = swap(s, "nav.tabs{position:fixed;left:0;right:0;bottom:0;z-index:6;background:var(--surface);border-top:1px solid var(--line);padding:6px 8px calc(6px + env(safe-area-inset-bottom,0px));display:flex;justify-content:space-around}",
            "nav.tabs{position:fixed;left:0;right:0;bottom:0;z-index:6;background:var(--surface);border-top:1px solid rgba(17,38,59,.8);padding:8px 8px calc(8px + env(safe-area-inset-bottom,0px));display:flex;justify-content:space-around;box-shadow:rgba(255,255,255,.06) 0 1px 0 0 inset}", 'nav')
s = swap(s, ".tab{flex:1;background:none;border:0;padding:6px 2px;display:flex;flex-direction:column;align-items:center;gap:2px;font-size:11px;font-weight:600;color:var(--muted);border-radius:10px}", ".tab{flex:1;background:none;border:0;padding:6px 2px;display:flex;flex-direction:column;align-items:center;gap:3px;font-size:10.5px;font-weight:400;letter-spacing:.02em;color:var(--muted);border-radius:12px}", 'tab')
s = swap(s, ".tab svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}", ".tab svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:1.4;stroke-linecap:round;stroke-linejoin:round}", 'tab svg')

# tables, filters, sheets, misc surfaces
s = swap(s, ".tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}", ".tablewrap{overflow-x:auto;border:1px solid rgba(17,38,59,.4);border-radius:var(--radius);background:var(--surface);box-shadow:var(--shadow)}", 'tablewrap')
s = swap(s, "th{position:sticky;top:0;background:var(--surface2);font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);cursor:pointer;user-select:none}", "th{position:sticky;top:0;background:var(--surface2);font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);cursor:pointer;user-select:none;font-weight:600}", 'th')
s = swap(s, "table{border-collapse:collapse;width:100%;min-width:900px;font-size:13px}", "table{border-collapse:collapse;width:100%;min-width:900px;font-size:13px;font-weight:300}", 'table')
s = swap(s, ".filters select,.filters input{border:1px solid var(--line);background:var(--surface);border-radius:10px;padding:7px 10px;font-size:13px}", ".filters select,.filters input{border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:12px;padding:8px 12px;font-size:13px}", 'filters')
s = swap(s, ".sheet{background:var(--surface);width:100%;max-width:640px;max-height:92vh;overflow:auto;border-radius:18px 18px 0 0;padding:16px 16px calc(24px + env(safe-area-inset-bottom,0px))}", ".sheet{background:var(--surface);width:100%;max-width:640px;max-height:92vh;overflow:auto;border-radius:40px 40px 0 0;padding:22px 20px calc(28px + env(safe-area-inset-bottom,0px));box-shadow:var(--shadow);border-top:1px solid rgba(17,38,59,.6)}", 'sheet')
s = swap(s, ".sheet-bg{position:fixed;inset:0;background:rgba(1,20,35,.55);z-index:20;display:flex;align-items:flex-end;justify-content:center}", ".sheet-bg{position:fixed;inset:0;background:rgba(0,8,20,.7);z-index:20;display:flex;align-items:flex-end;justify-content:center}", 'sheet bg')
s = swap(s, ".field input,.field select,.field textarea{border:1px solid var(--line);background:var(--bg);border-radius:10px;padding:9px 10px;font-size:15px;width:100%}", ".field input,.field select,.field textarea{border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:12px;padding:11px 12px;font-size:15px;width:100%;font-weight:300;box-shadow:var(--shadow-pressed)}", 'field')
s = swap(s, ".field label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}", ".field label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;font-weight:600}", 'field label')
s = swap(s, ".statusbtns button{border-radius:999px;padding:7px 12px;border:1px solid var(--line);background:var(--surface);font-size:13px;font-weight:600}", ".statusbtns button{border-radius:9999px;padding:8px 14px;border:1px solid var(--line);background:var(--surface);color:var(--ink2);font-size:13px;font-weight:400}", 'statusbtns')
s = swap(s, ".toast{position:fixed;left:50%;bottom:calc(84px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);background:var(--ink);color:var(--bg);padding:9px 14px;border-radius:999px;font-size:13px;z-index:30;box-shadow:var(--shadow)}", ".toast{position:fixed;left:50%;bottom:calc(84px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);background:var(--accent);color:#fff;padding:10px 16px;border-radius:9999px;font-size:13px;z-index:30}", 'toast')
s = swap(s, ".seg{display:inline-flex;border:1px solid var(--line);border-radius:10px;overflow:hidden}", ".seg{display:inline-flex;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--surface2)}", 'seg')
s = swap(s, ".seg button{border:0;background:var(--surface);padding:6px 10px;font-size:12.5px;font-weight:600;color:var(--muted)}", ".seg button{border:0;background:transparent;padding:7px 12px;font-size:12.5px;font-weight:400;color:var(--muted)}", 'seg button')
s = swap(s, ".tag{font-size:11px;padding:2px 7px;border-radius:6px;background:var(--surface2);color:var(--ink2)}", ".tag{font-size:11px;padding:3px 9px;border-radius:9999px;background:var(--surface2);color:var(--ink2);font-weight:400}", 'tag')
s = swap(s, ".score{min-width:40px;text-align:center;padding:4px 8px;border-radius:8px;font-weight:700;font-size:14px}", ".score{min-width:40px;text-align:center;padding:5px 10px;border-radius:12px;font-weight:600;font-size:14px;font-family:var(--font-display)}", 'score')
s = swap(s, ".script{font-size:16px;line-height:1.55;white-space:pre-line;padding:12px 14px;border-radius:12px;background:var(--surface2);margin-top:8px}", ".script{font-size:17px;line-height:1.55;white-space:pre-line;padding:16px 18px;border-radius:20px;background:var(--surface2);margin-top:10px;font-weight:200;box-shadow:var(--shadow-pressed)}", 'script')
s = swap(s, ".prompter .txt{flex:1;overflow:auto;padding:24px 20px calc(40vh + env(safe-area-inset-bottom,0px));white-space:pre-line;line-height:1.5;font-weight:500;text-wrap:pretty}", ".prompter .txt{flex:1;overflow:auto;padding:24px 20px calc(40vh + env(safe-area-inset-bottom,0px));white-space:pre-line;line-height:1.45;font-weight:200;letter-spacing:-.01em;text-wrap:pretty}", 'prompter')
s = swap(s, "svg.chart .pt{fill:var(--accent);stroke:var(--surface);stroke-width:2}", "svg.chart .pt{fill:var(--accent);stroke:var(--bg);stroke-width:2}", 'chart pt')
s = swap(s, ".tip{position:absolute;pointer-events:none;background:var(--ink);color:var(--bg);font-size:12px;padding:6px 8px;border-radius:8px;transform:translate(-50%,-120%);white-space:nowrap;display:none}", ".tip{position:absolute;pointer-events:none;background:var(--surface3);color:var(--ink);border:1px solid var(--line);font-size:12px;padding:6px 10px;border-radius:12px;transform:translate(-50%,-120%);white-space:nowrap;display:none}", 'tip')
s = swap(s, ".linkrow .r{color:var(--accent);font-weight:700;flex:none}", ".linkrow .r{color:var(--accent);font-weight:500;flex:none}", 'linkrow r')
s = swap(s, ".chips button{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:6px 11px;font-size:12.5px;font-weight:600;color:var(--ink2)}", ".chips button{border:1px solid var(--line);background:var(--surface2);border-radius:9999px;padding:7px 13px;font-size:12.5px;font-weight:400;color:var(--ink2)}", 'chips')
s = swap(s, ".bar .lab{display:flex;align-items:center;gap:7px;font-weight:600}", ".bar .lab{display:flex;align-items:center;gap:7px;font-weight:400}", 'bar lab')
s = swap(s, ".bar .track{height:10px;border-radius:999px;background:var(--surface2);overflow:hidden}", ".bar .track{height:10px;border-radius:9999px;background:var(--surface3);overflow:hidden;box-shadow:var(--shadow-pressed)}", 'bar track')
s = swap(s, ".storyline{font-size:13.5px;color:var(--ink2);white-space:pre-line}", ".storyline{font-size:14px;color:var(--ink2);white-space:pre-line;font-weight:300}", 'storyline')

# ---- hero: filled, tilted tags in the Today card ----
s = swap(s, 'function pillarChip(n){const p=PILLARS[n]||{short:\'P\'+n};return `<span class="chip" style="background:var(--surface2)"><span class="dot p${n}"></span>${esc(p.short)}</span>`;}',
            'function pillarChip(n,filled){const p=PILLARS[n]||{short:\'P\'+n};if(filled)return `<span class="chip tagfill p${n}">${esc(p.short)}</span>`;return `<span class="chip" style="background:var(--surface2);border-color:rgba(17,38,59,.6)"><span class="dot p${n}"></span>${esc(p.short)}</span>`;}', 'pillarChip')
s = swap(s, '<div class="meta" style="display:flex;gap:6px;flex-wrap:wrap;align-items:center"><span class="chip fmt">${esc(s.format)}${s.lane&&s.lane!==\'-\'?\' · Lane \'+esc(s.lane):\'\'}</span>${pillarChip(s.pillar)}<span class="chip ${esc(s.kind)}">${esc(s.kind)}</span><span class="chip ${esc(s.status)}">${esc(s.status)}</span><span class="small num">${esc(s.time)}</span></div>',
            '<div class="hero-tags"><span class="chip fmt">${esc(s.format)}${s.lane&&s.lane!==\'-\'?\' &middot; Lane \'+esc(s.lane):\'\'}</span>${pillarChip(s.pillar,true)}<span class="chip ${esc(s.kind)}">${esc(s.kind)}</span><span class="chip ${esc(s.status)}">${esc(s.status)}</span><span class="small num" style="margin-left:4px">${esc(s.time)}</span></div>', 'hero tags') if '<div class="meta" style="display:flex;gap:6px;flex-wrap:wrap;align-items:center"><span class="chip fmt">${esc(s.format)}${s.lane&&s.lane!==\'-\'?\' · Lane \'+esc(s.lane):\'\'}</span>${pillarChip(s.pillar)}' in s else s
# the middot may already be an entity
s = swap(s, '<div class="meta" style="display:flex;gap:6px;flex-wrap:wrap;align-items:center"><span class="chip fmt">${esc(s.format)}${s.lane&&s.lane!==\'-\'?\' &middot; Lane \'+esc(s.lane):\'\'}</span>${pillarChip(s.pillar)}<span class="chip ${esc(s.kind)}">${esc(s.kind)}</span><span class="chip ${esc(s.status)}">${esc(s.status)}</span><span class="small num">${esc(s.time)}</span></div>',
            '<div class="hero-tags"><span class="chip fmt">${esc(s.format)}${s.lane&&s.lane!==\'-\'?\' &middot; Lane \'+esc(s.lane):\'\'}</span>${pillarChip(s.pillar,true)}<span class="chip ${esc(s.kind)}">${esc(s.kind)}</span><span class="chip ${esc(s.status)}">${esc(s.status)}</span><span class="small num" style="margin-left:4px">${esc(s.time)}</span></div>', 'hero tags entity') if 'class="hero-tags"' not in s else s
assert 'class="hero-tags"' in s, 'hero tags not applied'

# scripts tab chips: fill the pillar tag
s = re.sub(r"(<span class=\"tag num\">\$\{sc\.order.*?)\$\{pillarChip\(s\.pillar\)\}", lambda m: m.group(1)+"${pillarChip(s.pillar,true)}", s, count=1)

assert "—" not in s
open(p, 'w', encoding='utf-8').write(s)
print('restyled')
