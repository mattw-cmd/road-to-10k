"""Build the Road to 10k dashboard page, the seed files for its store, and the project docs.

Single source of truth is plan.json. Run: python build.py
"""
import json, os, sys, io
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DOC = r"C:\Users\matth\My Drive\Mortgage Content Machine\Instagram"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

plan = json.load(open(os.path.join(HERE, "plan.json"), encoding="utf-8"))
S = plan["settings"]
P = {p["n"]: p for p in S["pillars"]}

# ---- patches to the plan text (fixes found in review) ----
for s in plan["slots"]:
    if s["id"] == "W4-02":
        s["angle"] = s["angle"].replace("Three rises this year did more", "This year's rate rises did more")
    if s["id"] == "W2-06":
        s["angle"] = s["angle"].replace(
            "In 2024 the forward guidance said no rises until 2024 and the cash rate went up 13 times before that. Borrowers remember.",
            "In 2021 the RBA said no rise until 2024. The first came in May 2022 and twelve more followed. Borrowers remember.")

# guard: no em dashes anywhere in the plan
raw = json.dumps(plan, ensure_ascii=False)
assert "\u2014" not in raw, "em dash found in plan.json"

# ---- 1. dashboard html ----
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
assert "\u2014" not in tpl, "em dash found in template"
plan_js = json.dumps(plan, ensure_ascii=False).replace("</", "<\\/")
html = tpl.replace("/*__PLAN__*/", plan_js)
open(os.path.join(HERE, "road-to-10k.html"), "w", encoding="utf-8").write(html)
print("dashboard:", len(html), "bytes")

# ---- 2. seed files for ArtifactData ----
seed = os.path.join(HERE, "seed")
os.makedirs(os.path.join(seed, "slots"), exist_ok=True)
for s in plan["slots"]:
    d = dict(s)
    d.setdefault("status", "PLANNED"); d.setdefault("metrics", {}); d.setdefault("skipReason", ""); d.setdefault("postedAt", ""); d.setdefault("notes", "")
    json.dump(d, open(os.path.join(seed, "slots", s["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"readings": plan["growth"], "updatedAt": "2026-09-16T12:00:00+10:00"}, open(os.path.join(seed, "growth-readings.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({k: v for k, v in S.items() if k != "pillars"} | {"pillars": S["pillars"], "weeks": plan["weeks"], "seededAt": "2026-09-16"}, open(os.path.join(seed, "meta-settings.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("seed files:", len(plan["slots"]) + 2)

# ---- 3. docs ----
def fmt(d):
    y, m, dd = map(int, d.split("-"))
    return date(y, m, dd).strftime("%a %d %b").replace(" 0", " ")

os.makedirs(OUT_DOC, exist_ok=True)

# Calendar
lines = ["# Instagram content calendar, two weeks ahead (from 16 Sep 2026)", "",
         f"{S['handle']} · {S['startFollowers']} followers on {fmt(S['startDate'])} · goal {S['goal']:,} by {fmt(S['goalDate'])} 2027",
         "", f"Weeks run **Wednesday to Tuesday**, aligned to the {S['batchDay']} batch day. Eight original posts a week: 4 reels, 4 carousels. Reels and carousels run independently. Stories daily.",
         "", "EVERGREEN films on batch day. TOPICAL gets a placeholder and a 15-minute filming window.", "",
         "## Pillars", ""]
for p in S["pillars"]:
    lines.append(f"{p['n']}. **{p['name']}**: {p['desc']}")
lines += ["", "Pillar 5 is not a fixed slot. One or two posts a week plus most Stories. Topicality beats symmetry.", ""]

for w in plan["weeks"]:
    slots = [s for s in plan["slots"] if s["week"] == w["id"]]
    lines += [f"## Week {w['n']} · {fmt(w['start'])} to {fmt(w['end'])} · batch {fmt(w['batch'])}", "", f"**Theme.** {w['theme']}", ""]
    if w.get("notes"):
        lines += [f"**Notes.** {w['notes']}", ""]
    if not slots:
        lines += ["_Themes only. Detailed slots arrive from the Sunday review one week ahead._", ""]
        continue
    lines += ["| ID | Date | Time | Format | Pillar | Kind | Working title | Hook | CTA |", "| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |"]
    for s in slots:
        lane = f" ({s['lane']})" if s.get("lane") and s["lane"] != "-" else ""
        lines.append(f"| {s['id']} | {fmt(s['date'])} | {s['time']} | {s['format']}{lane} | {s['pillar']} {P[s['pillar']]['short']} | {s['kind']} | {s['title']} | {s['hook']} | {s.get('cta') or ''} |")
    lines.append("")
    for s in slots:
        lines.append(f"**{s['id']} · {s['title']}.** {s['angle']}" + (f" _Window: {s['filmWindow']}_" if s.get("filmWindow") else ""))
        lines.append("")
    lines += ["**Story arcs**", ""]
    from datetime import timedelta
    y, m, dd = map(int, w["start"].split("-"))
    for i in range(7):
        d = (date(y, m, dd) + timedelta(days=i)).isoformat()
        if d in plan["stories"]:
            lines.append(f"- {fmt(d)}: {plan['stories'][d]}")
    lines.append("")

lines += ["", "## Australian moments to plan around", "", "| Date | Event | Confirmed | Use |", "| :-- | :-- | :-- | :-- |"]
for mo in plan["moments"]:
    lines.append(f"| {mo['date']} | {mo['event']} | {'yes' if mo['confirmed'] else 'no, confirm'} | {mo['use']} |")
lines += ["", "*General market commentary only, not advice. Everything here is a draft for review.*", ""]
cal = "\n".join(lines)
assert "\u2014" not in cal
open(os.path.join(OUT_DOC, "CONTENT CALENDAR - Two weeks ahead.md"), "w", encoding="utf-8").write(cal)

# Post log
log = ["# Instagram post log", "",
       "Running copy of the dashboard's post log. One row per planned slot. Appended by the Sunday review, never rewritten. `n/a` means not visible in Insights, never a guess.", "",
       "Rates are per unique account reached. Score is 50 at the trailing 20-post median for the format, 75 at double, 25 at half, provisional (*) under 8 posts.", "",
       "| ID | Date | Time | Format | Pillar | Title | Hook | Kind | CTA | Status | Skip | Reach | Views | Likes | Comments | Shares | Saves | Profile visits | Follows | Watch % | Share % | Save % | Follow % | Eng % | Score |",
       "| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |"]
for s in plan["slots"]:
    log.append(f"| {s['id']} | {s['date']} | {s['time']} | {s['format']} | {s['pillar']} {P[s['pillar']]['short']} | {s['title']} | {s['hook']} | {s['kind']} | {s.get('cta') or ''} | PLANNED |  | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
log += ["", "## Follower readings", "", "| Date | Followers | Source |", "| :-- | :-- | :-- |"]
for g in plan["growth"]:
    log.append(f"| {g['date']} | {g['count']} | {g['source']} |")
log += ["", "## Weekly reviews", "", "_First review Sunday 27 September 2026 on Week 1 (16 to 22 Sep)._", ""]
open(os.path.join(OUT_DOC, "POST LOG.md"), "w", encoding="utf-8").write("\n".join(log))

print("docs written to", OUT_DOC)
