import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = json.load(open('plan.json', encoding='utf-8'))
S = p['settings']

# ---- locked rhythm: pillar by day, same every week ----
S['horizonWeeks'] = 2
S['template'] = [
  {"day": "Wed", "format": "Reel", "lane": "A", "pillar": 2, "time": "12:30", "note": "The Number. One figure, one reveal. Topical lean, filmed on batch day from the freshest print."},
  {"day": "Thu", "format": "Carousel", "lane": "-", "pillar": 1, "time": "12:30", "note": "Economics behind the market, with the client implication."},
  {"day": "Fri", "format": "Reel", "lane": "B", "pillar": 4, "time": "06:45", "note": "Deal breakdown. The long one, 60 to 90 seconds, de-identified, told for clients."},
  {"day": "Sat", "format": "Carousel", "lane": "-", "pillar": 5, "time": "08:30", "note": "My journey. The 10k build in public, batch day, what went wrong."},
  {"day": "Sun", "format": "Carousel", "lane": "-", "pillar": 3, "time": "08:30", "note": "What the bank won't say, in slides. The Sunday scroll."},
  {"day": "Mon", "format": "Reel", "lane": "A", "pillar": 3, "time": "06:45", "note": "What the bank won't say, on camera. The antagonist reel opens the working week."},
  {"day": "Mon", "format": "Carousel", "lane": "-", "pillar": 2, "time": "17:30", "note": "The Number in slides. Data slide with three columns."},
  {"day": "Tue", "format": "Reel", "lane": "A", "pillar": 1, "time": "06:45", "note": "Economics reel, or the live react when a decision lands on a Tuesday (RBA)."}
]
S['templateRule'] = "Days and pillars are locked. Topics are not. A rate decision, lender policy change, APRA move, Budget, market print or viral property story takes the slot for that day in its pillar, or bumps the nearest slot if it does not fit any. Only two weeks are planned at a time: this week in detail, next week in detail, then themes only."

# ---- curated news sources and searches ----
gnews = "https://news.google.com/search?hl=en-AU&gl=AU&ceid=AU:en&q="
S['news'] = {
  "searches": [
    {"pillar": 1, "label": "RBA cash rate decision", "url": gnews + "RBA%20cash%20rate%20decision"},
    {"pillar": 1, "label": "Cotality home value index", "url": gnews + "Cotality%20home%20value%20index"},
    {"pillar": 1, "label": "ABS lending indicators", "url": gnews + "ABS%20lending%20indicators%20home%20loans"},
    {"pillar": 1, "label": "Auction clearance Sydney", "url": gnews + "Sydney%20auction%20clearance%20rate"},
    {"pillar": 1, "label": "Negative gearing", "url": gnews + "negative%20gearing%20Australia"},
    {"pillar": 1, "label": "Housing supply 1.2 million target", "url": gnews + "1.2%20million%20homes%20target"},
    {"pillar": 2, "label": "Rent to income record", "url": gnews + "Australia%20rent%20share%20of%20income%20record"},
    {"pillar": 2, "label": "Borrowing capacity fell", "url": gnews + "borrowing%20capacity%20Australia%20fallen"},
    {"pillar": 2, "label": "HECS borrowing power", "url": gnews + "HECS%20HELP%20debt%20borrowing%20power%20home%20loan"},
    {"pillar": 3, "label": "Banks cut variable rates new customers", "url": gnews + "banks%20cut%20variable%20rates%20new%20customers%20Australia"},
    {"pillar": 3, "label": "Loyalty tax mortgage", "url": gnews + "mortgage%20loyalty%20tax%20Australia"},
    {"pillar": 3, "label": "APRA serviceability buffer DTI", "url": gnews + "APRA%20serviceability%20buffer%20debt%20to%20income"},
    {"pillar": 3, "label": "Lender policy change brokers", "url": gnews + "lender%20policy%20change%20brokers%20Australia"},
    {"pillar": 3, "label": "Fixed rates cut raised", "url": gnews + "fixed%20home%20loan%20rates%20Australia%20cut"},
    {"pillar": 4, "label": "Self-employed home loan declined", "url": gnews + "self-employed%20home%20loan%20Australia"},
    {"pillar": 4, "label": "First home buyer 5% deposit scheme", "url": gnews + "5%25%20deposit%20scheme%20first%20home%20buyers"},
    {"pillar": 4, "label": "Private credit non-bank lenders", "url": gnews + "private%20credit%20Australia%20non-bank%20lender"}
  ],
  "sources": [
    {"label": "RBA media releases", "url": "https://www.rba.gov.au/media-releases/", "note": "Decision day 2:30pm. Read the statement, not the headline."},
    {"label": "RBA schedule", "url": "https://www.rba.gov.au/schedules-events/board-meeting-schedules.html", "note": "Next: 3 Nov, 8 Dec, 9 Feb."},
    {"label": "Cotality research", "url": "https://www.cotality.com/au/insights", "note": "Home Value Index first business day of the month. Rental report monthly."},
    {"label": "ABS Lending Indicators", "url": "https://www.abs.gov.au/statistics/economy/finance/lending-indicators/latest-release", "note": "Quarterly now. Next 11 Nov 11:30am."},
    {"label": "APRA news", "url": "https://www.apra.gov.au/news-and-publications", "note": "Buffer, DTI cap, macroprudential."},
    {"label": "Broker Daily", "url": "https://www.brokerdaily.au/", "note": "Lender policy changes before anyone else. Describe the mechanism, never name the lender."},
    {"label": "The Adviser", "url": "https://www.theadviser.com.au/", "note": "Broker channel news, aggregator data."},
    {"label": "Australian Broker", "url": "https://www.brokernews.com.au/", "note": "Policy round-ups."},
    {"label": "AFR Property", "url": "https://www.afr.com/property", "note": "The read the HNW audience has already seen. Find the angle under it."},
    {"label": "ABC News Business", "url": "https://www.abc.net.au/news/business", "note": "What your 25 to 35 audience actually reads. Their framing is your foil."},
    {"label": "Canstar rate moves", "url": "https://www.canstar.com.au/home-loans/", "note": "Who cut, who raised. Never quote a rate on camera."},
    {"label": "Domain auction results", "url": "https://www.domain.com.au/auction-results/sydney/", "note": "Saturday night clearance for the Sunday story."},
    {"label": "SQM Research", "url": "https://sqmresearch.com.au/", "note": "Vacancy rates and asking rents."},
    {"label": "Treasury housing", "url": "https://treasury.gov.au/policy-topics/housing", "note": "Help to Buy, Home Guarantee Scheme changes."}
  ],
  "angleTest": "The topic is never the differentiator, the angle is. Before you bank a story ask: what is the obvious take, and what is the number or mechanism underneath it that changes something for one person this week?"
}

# ---- week 2 remapped onto the locked rhythm ----
byid = {s['id']: s for s in p['slots']}
def mv(i, date, day, time, pillar=None, fmt=None, lane=None):
    s = byid[i]; s['date'] = date; s['day'] = day; s['time'] = time
    if pillar: s['pillar'] = pillar
    if fmt: s['format'] = fmt
    if lane: s['lane'] = lane
mv('W2-01', '2026-09-23', 'Wed', '12:30', pillar=2)          # Reel A, The Number: investor lending fell 8.6%
mv('W2-05', '2026-09-24', 'Thu', '12:30', pillar=1)          # Carousel, Economics: 1,432 homes
mv('W2-03', '2026-09-25', 'Fri', '06:45', pillar=4)          # Reel B, Deal: self-employed
mv('W2-04', '2026-09-26', 'Sat', '08:30', pillar=5)          # Carousel, Journey: batch day
mv('W2-02', '2026-09-27', 'Sun', '08:30', pillar=3)          # Carousel, Bank Won't Say: non-banks exist
byid['W2-02']['title'] = "The lender your bank hopes you never hear about"
byid['W2-02']['hook'] = "Your bank will never tell you there are 30 other places to get the loan."
byid['W2-02']['angle'] = "Most borrowers do not know non-bank lenders exist, and the bank that just said no has no reason to mention them. The comparison is not rate A versus rate B, it is getting in versus not getting in, and missing 12 to 24 months of growth costs more than a modest rate gap. Composite example, no lender named, no rates. Trade-off: non-banks reprice faster and some have fewer features."
byid['W2-02']['type'] = "contrarian"
# Mon reel: new antagonist reel replaces the RBA-forecast contrarian
w206 = byid['W2-06']
w206.update({"date": "2026-09-28", "day": "Mon", "time": "06:45", "format": "Reel", "lane": "A", "pillar": 3, "type": "contrarian",
  "title": "Two rates, one bank",
  "hook": "Your bank has two rates. One for you, one for the person who walked in yesterday.",
  "angle": "Loyalty tax, the day before the RBA decides. Dozens of lenders cut variable rates for new customers over the past month while existing customers sat still. The bank counts on you not asking. What to say on the phone, in one line, and why the fortnight around a decision is when they are most willing to move. Trade-off: a reprice rarely matches a full refinance, but it costs nothing. No rates quoted.",
  "kind": "TOPICAL", "filmWindow": "Films batch day Wed 23 Sep. Re-check on Sunday 27 Sep that banks are still cutting for new customers; if the market has turned, swap the first line.",
  "cta": "Send this to someone who hasn't called their bank in a year.", "disclaimer": "general",
  "onScreen": "One bank. Two rates. Guess which one is yours."})
mv('W2-07', '2026-09-28', 'Mon', '17:30', pillar=2)          # Carousel, The Number: DTI six times
mv('W2-08', '2026-09-29', 'Tue', '15:15', pillar=1)          # Reel A, Economics: RBA live react
for s in p['slots']:
    if s['week'] == 'W2': s['week'] = 'W2'

# ---- drop weeks 3 and 4 detail; keep themes to week 4 only ----
retired = [s['id'] for s in p['slots'] if s['week'] in ('W3', 'W4')]
p['slots'] = [s for s in p['slots'] if s['week'] in ('W1', 'W2')]
S['retiredSlots'] = retired
p['weeks'] = [w for w in p['weeks'] if w['id'] in ('W1', 'W2', 'W3', 'W4')]
for w in p['weeks']:
    if w['id'] == 'W2':
        w['theme'] = "RBA week on the locked rhythm. Investor lending fell off a cliff, 1,432 homes, the self-employed deal, loyalty tax the day before the decision, and a live react on Tuesday 29 Sep."
        w['notes'] = "NSW school holidays start Sat 26 Sep. RBA decision Tue 29 Sep 2:30pm, 15-minute filming window 2:45 to 3:00pm. Scripts for this week arrive with the Sunday 20 Sep import, or ask for them earlier. Batch films Wed 23 Sep."
    if w['id'] in ('W3', 'W4'):
        w['theme'] = "Themes only. Detailed slots come from the Sunday review one week ahead. " + w['theme']
# stories for weeks 3-4 go, weeks 1-2 stay
p['stories'] = {d: a for d, a in p['stories'].items() if d <= '2026-09-29'}
# week 2 story for Mon 28 mentions the swapped reel
p['stories']['2026-09-28'] = "AM: share W2-06, 'your bank has two rates', with 'RBA decides tomorrow, call today'. Midday: market pricing screenshot with the scenario disclaimer. PM: share W2-07, 'the number on your file'."

raw = json.dumps(p, ensure_ascii=False)
assert "—" not in raw
json.dump(p, open('plan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
from collections import Counter
print('slots:', len(p['slots']), 'retired:', len(retired))
for s in sorted(p['slots'], key=lambda x: (x['date'], x['time'])):
    if s['week'] == 'W2': print(s['id'], s['day'], s['date'], s['time'], s['format'], s['lane'], 'P' + str(s['pillar']), '|', s['title'])
