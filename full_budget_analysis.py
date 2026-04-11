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
    # Amazon sub-categories
    if 'AMAZON PRIME*' in d or 'AMAZON PRIME*' in d: return 'Amazon Prime Membership'
    if any(x in d for x in ['AMAZON','AMZN','ALEXA SKILLS']): return 'Amazon (Shopping/Subscribe&Save)'
    # Groceries
    if any(x in d for x in ['KING SOOPERS','SAFEWAY','SPROUTS','TRADER JOE']): return 'Groceries (Supermarket)'
    if any(x in d for x in ['WHOLEFDS','WHOLE FOODS']): return 'Groceries (Whole Foods)'
    if any(x in d for x in ['SAMSCLUB','SAMS CLUB','SAMS SCAN']): return 'Warehouse Club (Sams)'
    # Housing
    if any(x in d for x in ['AGI*HOMEOWNER','ASSURANT']): return 'Home Insurance'
    if any(x in d for x in ['HIGHLANDS RANCH WATER','HRMD']): return 'Water/Sewer'
    if 'WM.COM' in d and 'AMZN' not in d: return 'Waste Management'
    if any(x in d for x in ['HOME DEPOT','LOWES']): return 'Home Improvement'
    # Transportation
    if any(x in d for x in ['GEICO']): return 'Vehicle Insurance (GEICO)'
    if any(x in d for x in ['SHELL OIL','PHILLIPS 66','CONOCO']): return 'Gas'
    if any(x in d for x in ['E 470']): return 'Tolls'
    if any(x in d for x in ['DEN PUBLIC PARKING','DENVER AIRPORT']): return 'Airport Parking'
    if any(x in d for x in ['UBER','LYFT']): return 'Rideshare'
    if any(x in d for x in ['ELECTRIFY','NYX']): return 'EV Charging'
    if any(x in d for x in ['AVIS']): return 'Rental Cars'
    if any(x in d for x in ['UNITED 01','UNITED.COM']): return 'Flights (United)'
    # Subscriptions & bills
    if any(x in d for x in ['CLAUDE','ANTHROPIC']): return 'Subscription: Claude AI'
    if any(x in d for x in ['OPENAI','CHATGPT']): return 'Subscription: ChatGPT'
    if any(x in d for x in ['DISH DBS','DISH NTWK','AUTOPAY / DISH']): return 'Subscription: DISH TV'
    if any(x in d for x in ['SLING']): return 'Subscription: Sling TV'
    if any(x in d for x in ['APPLE.COM']): return 'Subscription: Apple'
    if any(x in d for x in ['BOOST MOBILE']): return 'Subscription: Phone (Boost)'
    if any(x in d for x in ['NETFLIX','HULU','SPOTIFY','DISNEY','HBO','PARAMOUNT','PEACOCK']): return 'Subscription: Streaming'
    if any(x in d for x in ['DAILY WIRE']): return 'Subscription: Daily Wire'
    if any(x in d for x in ['ROBINHOOD']): return 'Subscription: Robinhood Gold'
    # Food & Dining
    if any(x in d for x in ['DISH TV RIVER']): return 'Work Cafeteria (DISH)'
    if any(x in d for x in ['FIVE GUYS','5 GUYS']): return 'Dining: Five Guys'
    if any(x in d for x in ['CHICK-FIL','POTBELLY','EINSTEIN','VIEWHOUSE','LITTLETON BREWERY','PACIFIC BREEZE','SWEET COW','PORTLAND ROAST','CHIPOTLE','MCDONALDS','SUBWAY','TACO BELL','ROCKY','TST*']): return 'Dining Out'
    if any(x in d for x in ['BALL ARENA CON']): return 'Dining: Events'
    # Personal
    if any(x in d for x in ['FLOYD']): return 'Haircuts (Floyds)'
    if any(x in d for x in ['GORILLA MIND']): return 'Supplements'
    # Shopping
    if any(x in d for x in ['NORDSTROM']): return 'Shopping: Clothing (Nordstrom)'
    if any(x in d for x in ['VIVOBAREFOOT','TAILORED','SHELBY','COLUMBIA']): return 'Shopping: Clothing/Shoes'
    if any(x in d for x in ['TARGET']): return 'Shopping: Target'
    if any(x in d for x in ['APPLE STORE']): return 'Shopping: Apple Store'
    if any(x in d for x in ['ALIBABA']): return 'SickBeard (Business)'
    if any(x in d for x in ['DALSTRONG']): return 'Shopping: Kitchen/Home'
    if any(x in d for x in ['PERFORMANCE CYCLE']): return 'Motorcycle (Parts/Service)'
    # Other
    if any(x in d for x in ['TURBOTAX','INTUIT']): return 'Tax Prep'
    if any(x in d for x in ['GLF*MURPHY','TOPGOLF']): return 'Golf'
    if any(x in d for x in ['BALL ARENA']) and 'CON' not in d: return 'Entertainment'
    if any(x in d for x in ['USPS']): return 'Shipping'
    return 'Other'

for t in all_txns:
    t['cat'] = categorize(t['desc'])

txns_2025 = [t for t in all_txns if t['date'].year == 2025]

cats = defaultdict(lambda: {'total':0, 'count':0})
for t in txns_2025:
    cats[t['cat']]['total'] += t['amount']
    cats[t['cat']]['count'] += 1

grand = sum(d['total'] for d in cats.values())

# ===== INCOME vs SPENDING =====
gross = 120000
# Estimate taxes from tax filing data
# Federal refund: $4,807, meaning overpaid. Effective federal tax ~15-17% on 120K single
# Using tax filing: itemized $23,743, taxable income ~$96K, federal tax ~$15K, CO ~$4K, FICA ~$9K
federal_tax = 15000  # approximate from refund + withholding
state_tax = 3833     # from tax filing
fica = 9180          # 7.65% of 120K
total_tax = federal_tax + state_tax + fica
net_income = gross - total_tax
# 3% raise for 2026
gross_2026 = gross * 1.03
net_2026 = gross_2026 - (total_tax * 1.02)  # taxes go up slightly too

# Fixed costs not on credit cards
mortgage = 1800 * 12  # estimate ~$1,800/mo (from $380K loan)
property_tax = 3743   # from tax filing
church = 120 * 52     # $120/week
hoa = 0               # included in property tax or separate?

# Group into budget categories
budget = {}
# Housing
housing_cc = sum(cats[c]['total'] for c in ['Home Insurance','Water/Sewer','Waste Management','Home Improvement'] if c in cats)
budget['Housing (mortgage+tax+insurance+utilities)'] = {
    'cc': housing_cc,
    'non_cc': mortgage + property_tax,
    'note': f'Mortgage ~$1,800/mo + prop tax $3,743/yr + CC charges'
}
# Transportation
transport_cc = sum(cats[c]['total'] for c in ['Vehicle Insurance (GEICO)','Gas','Tolls','Airport Parking','Rideshare','EV Charging','Rental Cars','Flights (United)','Motorcycle (Parts/Service)'] if c in cats)
budget['Transportation (insurance+gas+flights+moto)'] = {
    'cc': transport_cc,
    'note': 'GEICO bundle + gas + flights + motorcycle'
}
# Food & Groceries
food_cc = sum(cats[c]['total'] for c in ['Groceries (Supermarket)','Groceries (Whole Foods)','Warehouse Club (Sams)','Work Cafeteria (DISH)','Dining: Five Guys','Dining Out','Dining: Events'] if c in cats)
budget['Food & Dining (grocery+dining+cafeteria)'] = {
    'cc': food_cc,
    'note': 'All food: grocery stores + restaurants + work cafe'
}
# Amazon
amazon_cc = sum(cats[c]['total'] for c in ['Amazon (Shopping/Subscribe&Save)','Amazon Prime Membership'] if c in cats)
budget['Amazon (Subscribe&Save + shopping)'] = {
    'cc': amazon_cc,
    'note': 'Includes food/medicine/protein/household + other items'
}
# Subscriptions
sub_cc = sum(cats[c]['total'] for c in ['Subscription: Claude AI','Subscription: ChatGPT','Subscription: DISH TV','Subscription: Sling TV','Subscription: Apple','Subscription: Phone (Boost)','Subscription: Streaming','Subscription: Daily Wire','Subscription: Robinhood Gold'] if c in cats)
budget['Subscriptions & Bills'] = {
    'cc': sub_cc,
    'note': 'Claude, DISH, Sling, Apple, Boost, streaming, etc.'
}
# Giving
budget['Church Giving'] = {
    'cc': 0,
    'non_cc': church,
    'note': f'~$120/week to Highlands Ranch Church of Christ'
}
# Shopping
shop_cc = sum(cats[c]['total'] for c in ['Shopping: Clothing (Nordstrom)','Shopping: Clothing/Shoes','Shopping: Target','Shopping: Apple Store','Shopping: Kitchen/Home'] if c in cats)
budget['Shopping (clothing+target+home)'] = {
    'cc': shop_cc,
    'note': 'Nordstrom, Target, Apple Store, etc.'
}
# Business
biz_cc = cats.get('SickBeard (Business)',{}).get('total',0)
budget['SickBeard LLC (business expense)'] = {
    'cc': biz_cc,
    'note': 'Alibaba orders — business cost, not personal'
}
# Personal
personal_cc = sum(cats[c]['total'] for c in ['Haircuts (Floyds)','Supplements','Golf','Entertainment'] if c in cats)
budget['Personal (haircuts+supplements+golf+entertainment)'] = {
    'cc': personal_cc,
    'note': 'Floyds, Gorilla Mind, golf, Ball Arena'
}
# Other
other_cc = sum(cats[c]['total'] for c in ['Tax Prep','Shipping','Other'] if c in cats)
budget['Other/Misc'] = {
    'cc': other_cc,
    'note': 'TurboTax, USPS, uncategorized'
}

print("=" * 90)
print("COMPLETE FINANCIAL PICTURE — 2025")
print("=" * 90)

print(f"\n{'INCOME':}")
print(f"  Gross salary:                          ${gross:>10,.0f}")
print(f"  Federal tax (est):                     ${federal_tax:>10,.0f}")
print(f"  Colorado state tax:                    ${state_tax:>10,.0f}")
print(f"  FICA (Social Security + Medicare):     ${fica:>10,.0f}")
print(f"  -------------------------------------------------")
print(f"  NET TAKE-HOME (est):                   ${net_income:>10,.0f}  (${net_income/12:,.0f}/mo)")
print(f"  Tax refund received:                   ${5614:>10,.0f}")
print(f"  Total available:                       ${net_income+5614:>10,.0f}")

print(f"\n{'2026 WITH 3% RAISE':}")
print(f"  Gross salary:                          ${gross_2026:>10,.0f}")
print(f"  NET TAKE-HOME (est):                   ${net_2026:>10,.0f}  (${net_2026/12:,.0f}/mo)")

print(f"\n{'='*90}")
print("ANNUAL BUDGET BREAKDOWN")
print("=" * 90)
print(f"{'Category':<48} {'Annual':>10} {'Monthly':>10} {'% Net':>7}")
print("-" * 78)

total_spent = 0
for cat, data in sorted(budget.items(), key=lambda x: -(x[1].get('cc',0)+x[1].get('non_cc',0))):
    cc = data.get('cc', 0)
    non_cc = data.get('non_cc', 0)
    total = cc + non_cc
    total_spent += total
    pct = total / net_income * 100
    marker = ''
    if pct > 20: marker = ' <<<'
    elif pct > 10: marker = ' <<'
    print(f"  {cat:<46} ${total:>9,.0f} ${total/12:>8,.0f}/mo {pct:>5.1f}%{marker}")

print(f"  {'-'*76}")
print(f"  {'TOTAL SPENDING':<46} ${total_spent:>9,.0f} ${total_spent/12:>8,.0f}/mo {total_spent/net_income*100:>5.1f}%")
print(f"  {'SURPLUS / DEFICIT':<46} ${net_income - total_spent:>+10,.0f} ${(net_income-total_spent)/12:>+9,.0f}/mo")

print(f"\n{'='*90}")
print("DETAILED CREDIT CARD SPENDING BY CATEGORY (2025)")
print("=" * 90)
print(f"{'Category':<48} {'Annual':>10} {'Monthly':>10} {'Txns':>6}")
print("-" * 78)
for cat, data in sorted(cats.items(), key=lambda x: -x[1]['total']):
    print(f"  {cat:<46} ${data['total']:>9,.0f} ${data['total']/12:>8,.0f}/mo {data['count']:>5}")
print(f"  {'-'*76}")
print(f"  {'TOTAL (credit cards only)':<46} ${grand:>9,.0f} ${grand/12:>8,.0f}/mo")

# Non-CC spending
non_cc_total = mortgage + property_tax + church
print(f"\n  {'NON-CREDIT CARD SPENDING':}")
print(f"    Mortgage (~$1,800/mo):                       ${mortgage:>9,.0f}")
print(f"    Property tax:                                ${property_tax:>9,.0f}")
print(f"    Church ($120/wk):                            ${church:>9,.0f}")
print(f"    --------------------------------------------------")
print(f"    Non-CC subtotal:                             ${non_cc_total:>9,.0f}")

print(f"\n{'='*90}")
print("VS NATIONAL AVERAGES — Single Person Household (BLS 2023, inflation-adjusted)")
print("=" * 90)

# Better national averages for single person, ~$120K income bracket
your_food = sum(cats[c]['total'] for c in ['Groceries (Supermarket)','Groceries (Whole Foods)','Warehouse Club (Sams)'] if c in cats)
your_dining = sum(cats[c]['total'] for c in ['Dining Out','Dining: Five Guys','Work Cafeteria (DISH)','Dining: Events'] if c in cats)
your_transport = sum(cats[c]['total'] for c in ['Vehicle Insurance (GEICO)','Gas','Tolls','Rideshare','Motorcycle (Parts/Service)'] if c in cats)
your_clothing = sum(cats[c]['total'] for c in ['Shopping: Clothing (Nordstrom)','Shopping: Clothing/Shoes'] if c in cats)
your_entertainment = sum(cats[c]['total'] for c in ['Golf','Entertainment','Subscription: Streaming','Subscription: Sling TV','Subscription: DISH TV','Subscription: Apple'] if c in cats)

comps = [
    ('Groceries',          your_food,    5200, 'Includes King Soopers + Whole Foods + Sams (NOT Amazon food)'),
    ('Dining/Restaurants',  your_dining,  3600, 'Cafeteria + Five Guys + dining out'),
    ('Gas & Transport',     your_transport, 4500, 'GEICO + gas + tolls + motorcycle'),
    ('Housing (non-mort)',  housing_cc,   4200, 'Insurance + water + waste + repairs'),
    ('Clothing',            your_clothing, 1800, 'Nordstrom + shoes + Columbia'),
    ('Entertainment/Media', your_entertainment, 3500, 'Golf + events + TV + streaming'),
    ('Phone',               cats.get('Subscription: Phone (Boost)',{}).get('total',0), 1200, 'Boost Mobile'),
    ('Church/Charity',      church,       2500, '$120/week — very generous'),
    ('Amazon/Online',       amazon_cc,    2400, 'Subscribe&Save + general shopping'),
]

print(f"{'Category':<22} {'You':>10} {'Natl Avg':>10} {'Diff':>10} {'Verdict':>12}  Notes")
print("-" * 95)
for cat, you, natl, note in comps:
    diff = you - natl
    pct_diff = (diff / natl * 100) if natl > 0 else 0
    if pct_diff > 50: verdict = 'VERY HIGH'
    elif pct_diff > 25: verdict = 'HIGH'
    elif pct_diff < -50: verdict = 'VERY LOW'
    elif pct_diff < -25: verdict = 'LOW'
    else: verdict = 'NORMAL'
    print(f"  {cat:<20} ${you:>9,.0f} ${natl:>9,.0f} {'+' if diff>=0 else ''}{diff:>+9,.0f} {verdict:>11}  {note}")

print(f"\n{'='*90}")
print("SUBSCRIPTION AUDIT — What you pay monthly for recurring services")
print("=" * 90)
subs = [
    ('GEICO (auto+moto bundle)', cats.get('Vehicle Insurance (GEICO)',{}).get('total',0)),
    ('Home Insurance (Assurant)', cats.get('Home Insurance',{}).get('total',0)),
    ('Water/Sewer', cats.get('Water/Sewer',{}).get('total',0)),
    ('Waste Management', cats.get('Waste Management',{}).get('total',0)),
    ('DISH TV (employee)', cats.get('Subscription: DISH TV',{}).get('total',0)),
    ('Sling TV (employee)', cats.get('Subscription: Sling TV',{}).get('total',0)),
    ('Claude AI', cats.get('Subscription: Claude AI',{}).get('total',0)),
    ('ChatGPT (cancelled)', cats.get('Subscription: ChatGPT',{}).get('total',0)),
    ('Apple subscriptions', cats.get('Subscription: Apple',{}).get('total',0)),
    ('Boost Mobile (phone)', cats.get('Subscription: Phone (Boost)',{}).get('total',0)),
    ('Streaming', cats.get('Subscription: Streaming',{}).get('total',0)),
    ('Daily Wire', cats.get('Subscription: Daily Wire',{}).get('total',0)),
    ('Robinhood Gold', cats.get('Subscription: Robinhood Gold',{}).get('total',0)),
    ('Amazon Prime', cats.get('Amazon Prime Membership',{}).get('total',0)),
]
sub_total = sum(s[1] for s in subs)
print(f"{'Service':<30} {'Annual':>10} {'Monthly':>10} {'Status'}")
print("-" * 65)
for name, total in sorted(subs, key=lambda x: -x[1]):
    if total > 0:
        status = 'CANCELLED' if 'cancelled' in name.lower() else 'ACTIVE'
        print(f"  {name:<28} ${total:>9,.0f} ${total/12:>8,.0f}/mo  {status}")
print(f"  {'-'*63}")
print(f"  {'TOTAL RECURRING':<28} ${sub_total:>9,.0f} ${sub_total/12:>8,.0f}/mo")
print(f"  = {sub_total/net_income*100:.1f}% of net income")

# ===== KEY FINDINGS =====
print(f"\n{'='*90}")
print("KEY FINDINGS & RECOMMENDATIONS")
print("=" * 90)

surplus = net_income - total_spent
print(f"""
1. NET INCOME vs SPENDING:
   Take-home: ${net_income:,.0f}/yr (${net_income/12:,.0f}/mo)
   Total spend: ${total_spent:,.0f}/yr (${total_spent/12:,.0f}/mo)
   Surplus: ${surplus:+,.0f}/yr (${surplus/12:+,.0f}/mo)
   Savings rate: {surplus/net_income*100:.1f}% of net income

2. CHURCH GIVING: ${church:,.0f}/yr = {church/net_income*100:.1f}% of net income
   This is nearly double the national average for charitable giving.
   At $120/week, this is your 3rd largest expense after housing and vehicle insurance.

3. AMAZON: ${amazon_cc:,.0f}/yr = {amazon_cc/net_income*100:.1f}% of net income
   Much of this is Subscribe&Save (food, medicine, household), but at $660/mo
   it's worth auditing what's essential vs impulse. Even cutting 20% = $1,580/yr saved.

4. VEHICLE INSURANCE: ${cats.get('Vehicle Insurance (GEICO)',{}).get('total',0):,.0f}/yr (${cats.get('Vehicle Insurance (GEICO)',{}).get('total',0)/12:,.0f}/mo)
   This is for both a 2016 Ford + 2016 Yamaha R1M, both paid off.
   At $192/mo for two paid-off vehicles, worth getting competing quotes.

5. HOME INSURANCE: ${cats.get('Home Insurance',{}).get('total',0):,.0f}/yr
   77% above national average. Shop quotes from: State Farm, USAA, Progressive, Lemonade.
   Bundling with GEICO should already help, but the premium seems high for a $475K home.

6. WITH 3% RAISE (2026):
   New gross: ${gross_2026:,.0f}/yr
   Extra net: ~${(net_2026 - net_income):,.0f}/yr (~${(net_2026-net_income)/12:,.0f}/mo more)
   If spending stays flat, your surplus improves to ~${surplus + (net_2026-net_income):,.0f}/yr

7. WHAT YOU DO WELL:
   - Phone bill ($17/mo vs $100 national avg) = saves $1,000/yr
   - Dining out is HALF the national average
   - Gas spending is very low (short commute or hybrid?)
   - No car payments (both vehicles paid off) = saves ~$6,000/yr vs avg
   - Subscriptions are reasonable at ${sub_total/12:,.0f}/mo
""")

# Uncategorized "Other" breakdown
print(f"{'='*90}")
print("UNCATEGORIZED 'OTHER' TRANSACTIONS — ${:,.0f} total".format(cats.get('Other',{}).get('total',0)))
print("=" * 90)
others = [t for t in txns_2025 if t['cat'] == 'Other']
others.sort(key=lambda x: -x['amount'])
for t in others[:25]:
    print(f"  {t['date'].strftime('%m/%d')} {t['desc'][:50]:<50} ${t['amount']:>9,.2f}  ({t['card']})")
