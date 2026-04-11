import csv, os, re, pdfplumber
from collections import defaultdict
from datetime import datetime

all_txns = []

# Amex Gold CSVs
amex_dir = "C:/Users/Exterminator/Downloads/Amex Gold Statements/"
for f in os.listdir(amex_dir):
    if f.endswith('.csv'):
        with open(amex_dir + f, 'r', encoding='utf-8-sig') as fh:
            for row in csv.DictReader(fh):
                try:
                    amt = float(row['Amount'])
                    if amt <= 0: continue
                    dt = datetime.strptime(row['Date'].strip(), '%m/%d/%Y')
                    all_txns.append({'date': dt, 'desc': row['Description'].strip(), 'amount': amt, 'card': 'Amex Gold'})
                except: pass

# PDF statements
for card, dpath in [
    ('United Explorer', 'C:/Users/Exterminator/Downloads/United Statements/'),
    ('Amazon Prime', 'C:/Users/Exterminator/Downloads/Amazon Prime Statements/'),
    ('Chase Freedom', 'C:/Users/Exterminator/Downloads/Freedom Statements/')
]:
    for fname in sorted(os.listdir(dpath)):
        if not fname.endswith('.pdf'): continue
        yr = fname[:4]
        with pdfplumber.open(dpath + fname) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ''
                for line in text.split('\n'):
                    m = re.match(r'(\d{2})/(\d{2})\s+(.+?)\s+([\d,]+\.\d{2})$', line.strip())
                    if m:
                        desc = m.group(3).strip()
                        if any(s in desc for s in ['Payment Thank','AUTOMATIC PAYMENT','AMAZON MKTPLACE PMTS']): continue
                        try:
                            amt = float(m.group(4).replace(',',''))
                            mo = int(m.group(1))
                            day = int(m.group(2))
                            file_yr = int(yr)
                            file_mo = int(fname[4:6])
                            txn_yr = file_yr - 1 if mo > file_mo else file_yr
                            dt = datetime(txn_yr, mo, day)
                            all_txns.append({'date': dt, 'desc': desc, 'amount': amt, 'card': card})
                        except: pass

def categorize(desc):
    d = desc.upper()
    if any(x in d for x in ['AMAZON','AMZN','ALEXA SKILLS']): return 'Amazon Shopping'
    if any(x in d for x in ['KING SOOPERS','SAFEWAY','SPROUTS','TRADER JOE']): return 'Groceries (Supermarket)'
    if any(x in d for x in ['WHOLEFDS','WHOLE FOODS']): return 'Groceries (Whole Foods)'
    if any(x in d for x in ['SAMSCLUB','SAMS CLUB','SAMS SCAN']): return 'Groceries (Sams Club)'
    if any(x in d for x in ['SHELL OIL','PHILLIPS 66','CONOCO']): return 'Gas'
    if any(x in d for x in ['GEICO']): return 'Auto Insurance'
    if any(x in d for x in ['CLAUDE','ANTHROPIC']): return 'AI (Claude)'
    if any(x in d for x in ['OPENAI','CHATGPT']): return 'AI (ChatGPT)'
    if any(x in d for x in ['DISH TV RIVER']): return 'Work Cafeteria'
    if any(x in d for x in ['DISH DBS','DISH NTWK','AUTOPAY / DISH']): return 'TV (DISH)'
    if any(x in d for x in ['SLING']): return 'TV (Sling)'
    if any(x in d for x in ['APPLE.COM']): return 'Apple Subscriptions'
    if any(x in d for x in ['APPLE STORE']): return 'Apple Store'
    if any(x in d for x in ['BOOST MOBILE']): return 'Phone (Boost)'
    if any(x in d for x in ['HIGHLANDS RANCH WATER','HRMD']): return 'Water/Sewer'
    if 'WM.COM' in d: return 'Waste Management'
    if any(x in d for x in ['NETFLIX','HULU','SPOTIFY','DISNEY','HBO','PARAMOUNT','PEACOCK','DAILY WIRE']): return 'Streaming'
    if any(x in d for x in ['UNITED 01','UNITED.COM']): return 'Flights'
    if any(x in d for x in ['DEN PUBLIC PARKING','DENVER AIRPORT']): return 'Airport/Parking'
    if any(x in d for x in ['E 470']): return 'Tolls'
    if any(x in d for x in ['FIVE GUYS','5 GUYS']): return 'Dining (Five Guys)'
    if any(x in d for x in ['FLOYD']): return 'Haircuts'
    if any(x in d for x in ['AGI*HOMEOWNER','ASSURANT']): return 'Home Insurance'
    if any(x in d for x in ['CHICK-FIL','POTBELLY','EINSTEIN','VIEWHOUSE','LITTLETON BREWERY','PACIFIC BREEZE','SWEET COW','PORTLAND ROAST','CHIPOTLE','MCDONALDS','SUBWAY','TACO BELL','ROCKY','BALL ARENA CON','TST*']): return 'Dining Out'
    if any(x in d for x in ['BALL ARENA']): return 'Entertainment'
    if any(x in d for x in ['TARGET']): return 'Target'
    if any(x in d for x in ['USPS']): return 'Shipping'
    if any(x in d for x in ['UBER','LYFT']): return 'Rideshare'
    if any(x in d for x in ['GORILLA MIND']): return 'Supplements'
    if any(x in d for x in ['TURBOTAX','INTUIT']): return 'Tax Prep'
    if any(x in d for x in ['NORDSTROM','VIVOBAREFOOT','TAILORED','SHELBY']): return 'Clothing/Shoes'
    if any(x in d for x in ['HOME DEPOT','LOWES']): return 'Home Improvement'
    if any(x in d for x in ['ELECTRIFY','NYX']): return 'EV Charging'
    if any(x in d for x in ['GLF*MURPHY','TOPGOLF']): return 'Golf'
    if any(x in d for x in ['ALIBABA']): return 'Alibaba'
    if any(x in d for x in ['ROBINHOOD']): return 'Robinhood Gold'
    return 'Other'

for t in all_txns:
    t['cat'] = categorize(t['desc'])

txns_2025 = [t for t in all_txns if t['date'].year == 2025]
txns_2026 = [t for t in all_txns if t['date'].year == 2026]

cats_2025 = defaultdict(lambda: {'total':0, 'count':0})
for t in txns_2025:
    cats_2025[t['cat']]['total'] += t['amount']
    cats_2025[t['cat']]['count'] += 1

grand_2025 = sum(d['total'] for d in cats_2025.values())

print("=" * 85)
print("FULL YEAR 2025 SPENDING BREAKDOWN")
print(f"Total: ${grand_2025:,.0f} across {sum(d['count'] for d in cats_2025.values())} transactions")
print("=" * 85)
print(f"{'Category':<28} {'Annual':>10} {'Monthly':>10} {'% Total':>8} {'Txns':>6}")
print("-" * 68)
for cat, data in sorted(cats_2025.items(), key=lambda x: -x[1]['total']):
    pct = (data['total'] / grand_2025 * 100) if grand_2025 > 0 else 0
    print(f"{cat:<28} ${data['total']:>9,.0f} ${data['total']/12:>8,.0f}/mo {pct:>6.1f}%  {data['count']:>5}")

# Monthly trend
print("\n" + "=" * 85)
print("MONTHLY SPENDING TREND (2025)")
print("=" * 85)
monthly = defaultdict(float)
for t in txns_2025:
    monthly[t['date'].strftime('%Y-%m')] += t['amount']
for m in sorted(monthly.keys()):
    bar = '#' * int(monthly[m] / 100)
    print(f"{m}: ${monthly[m]:>8,.0f} {bar}")
print(f"\nMonthly average: ${grand_2025/12:,.0f}")

# Quarterly
print("\n" + "=" * 85)
print("QUARTERLY SPENDING (2025)")
print("=" * 85)
quarterly = defaultdict(float)
for t in txns_2025:
    q = (t['date'].month - 1) // 3 + 1
    quarterly[f"Q{q}"] += t['amount']
for q in ['Q1','Q2','Q3','Q4']:
    print(f"{q}: ${quarterly.get(q,0):>10,.0f}")

# Needs vs Wants
needs_cats = ['Auto Insurance','Home Insurance','Water/Sewer','Waste Management','Gas','Phone (Boost)','Groceries (Supermarket)','Groceries (Whole Foods)','Groceries (Sams Club)','Tax Prep','TV (DISH)','Flights']
wants_cats = ['Amazon Shopping','Dining Out','Dining (Five Guys)','Entertainment','Streaming','TV (Sling)','Apple Subscriptions','Apple Store','AI (Claude)','AI (ChatGPT)','Golf','Clothing/Shoes','Supplements','Target','Haircuts','Rideshare','Alibaba','Work Cafeteria','EV Charging','Robinhood Gold','Shipping']

needs_total = sum(cats_2025[c]['total'] for c in needs_cats if c in cats_2025)
wants_total = sum(cats_2025[c]['total'] for c in wants_cats if c in cats_2025)
other_total = grand_2025 - needs_total - wants_total

print("\n" + "=" * 85)
print("NEEDS vs WANTS vs OTHER (2025)")
print("=" * 85)
print(f"{'Needs (bills/insurance/groceries/gas):':<45} ${needs_total:>9,.0f} ({needs_total/grand_2025*100:.1f}%)")
print(f"{'Wants (dining/shopping/entertainment/subs):':<45} ${wants_total:>9,.0f} ({wants_total/grand_2025*100:.1f}%)")
print(f"{'Other/Mixed:':<45} ${other_total:>9,.0f} ({other_total/grand_2025*100:.1f}%)")

# Top merchants
print("\n" + "=" * 85)
print("TOP 20 MERCHANTS BY SPEND (2025)")
print("=" * 85)
merchants = defaultdict(float)
for t in txns_2025:
    d = t['desc'].upper()
    if 'AMAZON' in d or 'AMZN' in d or 'ALEXA' in d: name = 'Amazon'
    elif 'KING SOOPERS' in d: name = 'King Soopers'
    elif 'SAMSCLUB' in d or 'SAMS CLUB' in d: name = "Sams Club"
    elif 'SHELL OIL' in d: name = 'Shell Gas'
    elif 'GEICO' in d: name = 'GEICO'
    elif 'WHOLEFDS' in d or 'WHOLE FOODS' in d: name = 'Whole Foods'
    elif 'AGI*HOMEOWNER' in d: name = 'Assurant Home Ins'
    elif 'WM.COM' in d: name = 'WM Waste Mgmt'
    elif 'DISH TV RIVER' in d: name = 'DISH Cafeteria'
    elif 'DISH DBS' in d or 'DISH NTWK' in d or 'AUTOPAY / DISH' in d: name = 'DISH TV'
    elif 'CLAUDE' in d or 'ANTHROPIC' in d: name = 'Claude AI'
    elif 'OPENAI' in d: name = 'OpenAI'
    elif 'HIGHLANDS' in d or 'HRMD' in d: name = 'Water/Sewer'
    elif 'BOOST MOBILE' in d: name = 'Boost Mobile'
    elif 'SLING' in d: name = 'Sling TV'
    elif 'APPLE.COM' in d: name = 'Apple.com'
    elif 'TARGET' in d: name = 'Target'
    elif 'FIVE GUYS' in d: name = 'Five Guys'
    elif 'FLOYD' in d: name = 'Floyds Barber'
    elif 'E 470' in d: name = 'E-470 Tolls'
    elif 'DEN PUBLIC' in d: name = 'DEN Parking'
    elif 'DENVER AIRPORT' in d: name = 'Denver Airport'
    else: name = t['desc'][:30]
    merchants[name] += t['amount']

for i, (name, total) in enumerate(sorted(merchants.items(), key=lambda x: -x[1])[:20]):
    print(f"{i+1:>2}. {name:<25} ${total:>9,.0f} (${total/12:>7,.0f}/mo)")

# National avg comparison (BLS 2023 single person ~$42K/yr)
print("\n" + "=" * 85)
print("VS NATIONAL AVERAGES (BLS Consumer Expenditure Survey, single person household)")
print("=" * 85)
natl = {
    'Groceries': 5200,
    'Dining Out': 3600,
    'Gas': 2100,
    'Auto Insurance': 1800,
    'Entertainment': 3500,
    'Phone': 1200,
    'Streaming/TV': 1200,
    'Clothing': 1600,
    'Home Insurance': 1500,
}
your = {
    'Groceries': sum(cats_2025[c]['total'] for c in ['Groceries (Supermarket)','Groceries (Whole Foods)','Groceries (Sams Club)'] if c in cats_2025),
    'Dining Out': sum(cats_2025[c]['total'] for c in ['Dining Out','Dining (Five Guys)','Work Cafeteria'] if c in cats_2025),
    'Gas': cats_2025.get('Gas',{}).get('total',0),
    'Auto Insurance': cats_2025.get('Auto Insurance',{}).get('total',0),
    'Entertainment': sum(cats_2025[c]['total'] for c in ['Entertainment','Golf'] if c in cats_2025),
    'Phone': cats_2025.get('Phone (Boost)',{}).get('total',0),
    'Streaming/TV': sum(cats_2025[c]['total'] for c in ['Streaming','TV (DISH)','TV (Sling)','Apple Subscriptions'] if c in cats_2025),
    'Clothing': cats_2025.get('Clothing/Shoes',{}).get('total',0),
    'Home Insurance': cats_2025.get('Home Insurance',{}).get('total',0),
}
print(f"{'Category':<20} {'You':>10} {'Natl Avg':>10} {'Diff':>10} {'Verdict':>15}")
print("-" * 68)
for cat in natl:
    y = your.get(cat, 0)
    n = natl[cat]
    diff = y - n
    if diff > n * 0.3: verdict = 'HIGH'
    elif diff < -n * 0.3: verdict = 'BELOW AVG'
    else: verdict = 'NORMAL'
    print(f"{cat:<20} ${y:>9,.0f} ${n:>9,.0f} {'+' if diff>=0 else ''}{diff:>+9,.0f}  {verdict:>14}")

# 2026 pace
if txns_2026:
    grand_2026 = sum(t['amount'] for t in txns_2026)
    months_2026 = max(1, len(set(t['date'].strftime('%Y-%m') for t in txns_2026)))
    projected = (grand_2026 / months_2026) * 12
    print(f"\n{'='*85}")
    print(f"2026 YTD (Jan-Mar): ${grand_2026:,.0f} ({months_2026} months)")
    print(f"Projected 2026 annual: ${projected:,.0f}")
    diff = projected - grand_2025
    print(f"vs 2025 actual: ${grand_2025:,.0f} ({'UP' if diff > 0 else 'DOWN'} ${abs(diff):,.0f} / {abs(diff)/grand_2025*100:.1f}%)")

# Subscription audit
print(f"\n{'='*85}")
print("RECURRING SUBSCRIPTIONS AUDIT (2025)")
print("=" * 85)
subs = {
    'Claude AI': cats_2025.get('AI (Claude)',{}).get('total',0),
    'ChatGPT': cats_2025.get('AI (ChatGPT)',{}).get('total',0),
    'DISH TV': cats_2025.get('TV (DISH)',{}).get('total',0),
    'Sling TV': cats_2025.get('TV (Sling)',{}).get('total',0),
    'Apple Subs': cats_2025.get('Apple Subscriptions',{}).get('total',0),
    'Boost Mobile': cats_2025.get('Phone (Boost)',{}).get('total',0),
    'Waste Mgmt': cats_2025.get('Waste Management',{}).get('total',0),
    'Water/Sewer': cats_2025.get('Water/Sewer',{}).get('total',0),
    'GEICO': cats_2025.get('Auto Insurance',{}).get('total',0),
    'Streaming': cats_2025.get('Streaming',{}).get('total',0),
    'Robinhood Gold': cats_2025.get('Robinhood Gold',{}).get('total',0),
}
sub_total = sum(subs.values())
print(f"{'Subscription':<20} {'Annual':>10} {'Monthly':>10}")
print("-" * 42)
for name, total in sorted(subs.items(), key=lambda x: -x[1]):
    if total > 0:
        print(f"{name:<20} ${total:>9,.0f} ${total/12:>8,.0f}/mo")
print(f"{'TOTAL SUBS':<20} ${sub_total:>9,.0f} ${sub_total/12:>8,.0f}/mo")
print(f"\nSubscriptions = {sub_total/grand_2025*100:.1f}% of total spending")
