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

for card, dpath in [
    ('United Explorer', 'C:/Users/Exterminator/Downloads/United Statements/'),
    ('Amazon Prime', 'C:/Users/Exterminator/Downloads/Amazon Prime Statements/'),
    ('Chase Freedom', 'C:/Users/Exterminator/Downloads/Freedom Statements/')
]:
    for fname in sorted(os.listdir(dpath)):
        if not fname.endswith('.pdf'): continue
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
                            file_yr = int(fname[:4])
                            file_mo = int(fname[4:6])
                            txn_yr = file_yr - 1 if mo > file_mo else file_yr
                            dt = datetime(txn_yr, mo, day)
                            all_txns.append({'date': dt, 'desc': desc, 'amount': amt, 'card': card})
                        except: pass

def categorize(desc):
    d = desc.upper()
    if 'AMAZON PRIME*' in d: return 'Amazon Prime Membership'
    if any(x in d for x in ['AMAZON','AMZN','ALEXA SKILLS']): return 'Amazon'
    if any(x in d for x in ['KING SOOPERS','SAFEWAY','SPROUTS','TRADER JOE']): return 'Groceries'
    if any(x in d for x in ['WHOLEFDS','WHOLE FOODS']): return 'Groceries'
    if any(x in d for x in ['SAMSCLUB','SAMS CLUB','SAMS SCAN']): return 'Groceries'
    if any(x in d for x in ['SHELL OIL','PHILLIPS 66','CONOCO']): return 'Gas'
    if any(x in d for x in ['GEICO']): return 'Vehicle Insurance'
    if any(x in d for x in ['AGI*HOMEOWNER','ASSURANT']): return 'Home Insurance'
    if any(x in d for x in ['HIGHLANDS RANCH WATER','HRMD','CENTENNIAL WATER']): return 'Water/Sewer'
    if 'WM.COM' in d and 'AMZN' not in d: return 'Waste Mgmt'
    if any(x in d for x in ['CLAUDE','ANTHROPIC','OPENAI','CHATGPT']): return 'AI Subs'
    if any(x in d for x in ['DISH TV RIVER']): return 'Work Cafeteria'
    if any(x in d for x in ['DISH DBS','DISH NTWK','AUTOPAY / DISH']): return 'DISH TV'
    if any(x in d for x in ['SLING']): return 'Sling TV'
    if any(x in d for x in ['APPLE.COM']): return 'Apple Subs'
    if any(x in d for x in ['BOOST MOBILE']): return 'Phone'
    if any(x in d for x in ['FIVE GUYS','CHICK-FIL','POTBELLY','EINSTEIN','VIEWHOUSE','LITTLETON BREWERY','PACIFIC BREEZE','SWEET COW','PORTLAND ROAST','CHIPOTLE','MCDONALDS','SUBWAY','TACO BELL','ROCKY','TST*','PARRY','DAVIDSONS','THAI BASIL','BALL ARENA CON']): return 'Dining Out'
    if any(x in d for x in ['NETFLIX','HULU','SPOTIFY','DISNEY','HBO','PARAMOUNT','PEACOCK','DAILY WIRE']): return 'Streaming'
    if any(x in d for x in ['UNITED 01','UNITED.COM']): return 'Flights'
    if any(x in d for x in ['DEN PUBLIC PARKING','DENVER AIRPORT']): return 'Airport'
    if any(x in d for x in ['E 470']): return 'Tolls'
    if any(x in d for x in ['FLOYD']): return 'Haircuts'
    if any(x in d for x in ['NORDSTROM','VIVOBAREFOOT','TAILORED','SHELBY','COLUMBIA','NIKE']): return 'Clothing'
    if any(x in d for x in ['TARGET']): return 'Target'
    if any(x in d for x in ['APPLE STORE']): return 'Apple Store'
    if any(x in d for x in ['ALIBABA']): return 'SickBeard Biz'
    if any(x in d for x in ['PERFORMANCE CYCLE']): return 'Motorcycle'
    if any(x in d for x in ['HOME DEPOT','LOWES','GENERAL AIR']): return 'Home Maint'
    if any(x in d for x in ['AVIS']): return 'Rental Cars'
    if any(x in d for x in ['GLF*MURPHY','TOPGOLF']): return 'Golf'
    if any(x in d for x in ['GORILLA MIND']): return 'Supplements'
    if any(x in d for x in ['TURBOTAX','INTUIT']): return 'Tax Prep'
    if any(x in d for x in ['UBER','LYFT']): return 'Rideshare'
    if any(x in d for x in ['USPS']): return 'Shipping'
    if any(x in d for x in ['ROBINHOOD']): return 'RH Gold'
    if any(x in d for x in ['CO MOTOR VEHICLE']): return 'Vehicle Reg'
    if any(x in d for x in ['MEMBERSHIP FEE','ANNUAL MEMBERSHIP']): return 'Card Fees'
    if any(x in d for x in ['DAYS INN','CONCEPT SURF','VAPEWH','EBAY','PAYPAL','CLEVERBRIDGE','AUTONATION','DALSTRONG']): return 'Other Shopping'
    return 'Other'

for t in all_txns:
    t['cat'] = categorize(t['desc'])

txns_2025 = [t for t in all_txns if t['date'].year == 2025]

# ========== MONTHLY BY CATEGORY ==========
print("=" * 130)
print("MONTHLY SPENDING BY CATEGORY (2025)")
print("=" * 130)

# Get top categories
cat_totals = defaultdict(float)
for t in txns_2025:
    cat_totals[t['cat']] += t['amount']
top_cats = [c for c, _ in sorted(cat_totals.items(), key=lambda x: -x[1]) if _ > 100]

# Build monthly grid
monthly_cats = defaultdict(lambda: defaultdict(float))
monthly_totals = defaultdict(float)
for t in txns_2025:
    m = t['date'].strftime('%b')
    monthly_cats[t['cat']][m] = monthly_cats[t['cat']].get(m, 0) + t['amount']
    monthly_totals[m] += t['amount']

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# Header
hdr = f"{'Category':<18}"
for m in months:
    hdr += f" {m:>6}"
hdr += f" {'TOTAL':>8} {'AVG':>7}"
print(hdr)
print("-" * 130)

for cat in top_cats:
    row = f"{cat:<18}"
    total = 0
    for m in months:
        val = monthly_cats[cat].get(m, 0)
        total += val
        if val > 0:
            row += f" ${val:>5,.0f}"
        else:
            row += f"     -"
    row += f" ${total:>7,.0f} ${total/12:>5,.0f}"
    print(row)

# Total row
row = f"{'TOTAL':<18}"
for m in months:
    val = monthly_totals.get(m, 0)
    row += f" ${val:>5,.0f}"
grand = sum(monthly_totals.values())
row += f" ${grand:>7,.0f} ${grand/12:>5,.0f}"
print("-" * 130)
print(row)

# ========== QUARTERLY BY CATEGORY ==========
print(f"\n{'='*90}")
print("QUARTERLY SPENDING BY CATEGORY (2025)")
print("=" * 90)

q_cats = defaultdict(lambda: defaultdict(float))
q_totals = defaultdict(float)
for t in txns_2025:
    q = f"Q{(t['date'].month-1)//3+1}"
    q_cats[t['cat']][q] = q_cats[t['cat']].get(q, 0) + t['amount']
    q_totals[q] += t['amount']

hdr = f"{'Category':<22} {'Q1':>10} {'Q2':>10} {'Q3':>10} {'Q4':>10} {'TOTAL':>10}"
print(hdr)
print("-" * 75)
for cat in top_cats:
    row = f"{cat:<22}"
    total = 0
    for q in ['Q1','Q2','Q3','Q4']:
        val = q_cats[cat].get(q, 0)
        total += val
        row += f" ${val:>9,.0f}" if val > 0 else f"        -"
    row += f" ${total:>9,.0f}"
    print(row)
print("-" * 75)
row = f"{'TOTAL':<22}"
for q in ['Q1','Q2','Q3','Q4']:
    row += f" ${q_totals.get(q,0):>9,.0f}"
row += f" ${grand:>9,.0f}"
print(row)

# ========== INCOME vs SPENDING - CORRECTED ==========
print(f"\n{'='*90}")
print("INCOME vs SPENDING — REALITY CHECK (2025)")
print("=" * 90)

gross = 120000
federal_tax = 15000
state_tax = 3833
fica = 9180
net = gross - federal_tax - state_tax - fica

# NON-CC fixed costs
mortgage = 1800 * 12  # ~$1,800/mo
prop_tax = 3743
church = 120 * 52

# CC spending
cc_total = grand

# One-time big expenses in the data
sickbeard = cat_totals.get('SickBeard Biz', 0)
motorcycle = cat_totals.get('Motorcycle', 0)
rental_cars = cat_totals.get('Rental Cars', 0)
card_fees = cat_totals.get('Card Fees', 0)

# Recurring vs one-time
one_time = sickbeard + motorcycle + rental_cars + card_fees + cat_totals.get('Other Shopping', 0) + cat_totals.get('Tax Prep', 0)
recurring_cc = cc_total - one_time

print(f"""
  GROSS INCOME:                    $120,000/yr   ($10,000/mo)
  - Federal tax:                   - $15,000
  - Colorado tax:                  -  $3,833
  - FICA:                         -  $9,180
  -----------------------------------------------
  NET TAKE-HOME:                    $91,987/yr   ( $7,666/mo)

  FIXED COSTS (non-CC):
    Mortgage:                      - $21,600/yr  (- $1,800/mo)
    Property tax:                  -  $3,743/yr  (-   $312/mo)
    Church:                        -  $6,240/yr  (-   $520/mo)
    Subtotal:                      - $31,583/yr  (- $2,632/mo)

  CREDIT CARD SPENDING:
    Recurring (bills/food/subs):   - ${recurring_cc:,.0f}/yr  (- ${recurring_cc/12:,.0f}/mo)
    One-time (moto/biz/travel):    -  ${one_time:,.0f}/yr  (variable)
    Subtotal:                      - ${cc_total:,.0f}/yr  (- ${cc_total/12:,.0f}/mo)

  -----------------------------------------------
  TOTAL OUT:                       - ${31583 + cc_total:,.0f}/yr  (- ${(31583+cc_total)/12:,.0f}/mo)

  SURPLUS:                          ${net - 31583 - cc_total:+,.0f}/yr  ( ${(net-31583-cc_total)/12:+,.0f}/mo)
  SAVINGS RATE:                     {(net-31583-cc_total)/net*100:.1f}% of net

  2026 ADJUSTMENTS:
    + 3% raise:                    +  $3,040/yr net
    - Sewer repair ($21K):         - $21,000 (one-time)
    - ChatGPT cancelled:           +    $240/yr saved
    -----------------------------------------------
    2026 will be a DEFICIT year due to sewer repair.
    Without sewer: surplus would be ~${net+3040-31583-recurring_cc:+,.0f}/yr
    With sewer:    deficit of ~${net+3040-31583-recurring_cc-21000:+,.0f} for 2026
""")

# ========== WHERE DOES EVERY DOLLAR GO ==========
print("=" * 90)
print("WHERE EVERY DOLLAR OF NET INCOME GOES (2025)")
print("=" * 90)

buckets = [
    ('Mortgage + Property Tax', mortgage + prop_tax, None),
    ('Church', church, None),
    ('Amazon (food/household/shopping)', cat_totals.get('Amazon', 0) + cat_totals.get('Amazon Prime Membership', 0), 'Audit Subscribe&Save'),
    ('Groceries (King Soopers/WF/Sams)', sum(cat_totals.get(c,0) for c in ['Groceries']), None),
    ('Vehicle Insurance (GEICO bundle)', cat_totals.get('Vehicle Insurance', 0), 'Shop quotes'),
    ('Home Insurance (Assurant)', cat_totals.get('Home Insurance', 0), 'Shop quotes'),
    ('SickBeard (business)', cat_totals.get('SickBeard Biz', 0), 'Business expense'),
    ('Dining Out (all restaurants)', cat_totals.get('Dining Out', 0), None),
    ('Motorcycle (Performance Cycle)', cat_totals.get('Motorcycle', 0), 'One-time?'),
    ('Clothing (Nordstrom/Nike/etc)', cat_totals.get('Clothing', 0), None),
    ('Rental Cars (Avis)', cat_totals.get('Rental Cars', 0), 'Travel'),
    ('Water/Sewer', cat_totals.get('Water/Sewer', 0), None),
    ('Flights (United)', cat_totals.get('Flights', 0), None),
    ('Gas', cat_totals.get('Gas', 0), None),
    ('Waste Management', cat_totals.get('Waste Mgmt', 0), None),
    ('AI Subscriptions', cat_totals.get('AI Subs', 0), 'ChatGPT cancelled'),
    ('Work Cafeteria', cat_totals.get('Work Cafeteria', 0), None),
    ('Haircuts (Floyds)', cat_totals.get('Haircuts', 0), None),
    ('Target', cat_totals.get('Target', 0), None),
    ('Golf', cat_totals.get('Golf', 0), None),
    ('Card Annual Fees', cat_totals.get('Card Fees', 0), 'Amex $325 + United $95'),
    ('DISH TV (employee)', cat_totals.get('DISH TV', 0), None),
    ('Home Maintenance', cat_totals.get('Home Maint', 0), None),
    ('Apple Subs', cat_totals.get('Apple Subs', 0), None),
    ('Phone (Boost $17/mo)', cat_totals.get('Phone', 0), None),
    ('Sling TV (employee)', cat_totals.get('Sling TV', 0), None),
    ('Supplements', cat_totals.get('Supplements', 0), None),
    ('Tax Prep', cat_totals.get('Tax Prep', 0), None),
    ('Airport Parking', cat_totals.get('Airport', 0), None),
    ('Streaming', cat_totals.get('Streaming', 0), None),
    ('Tolls', cat_totals.get('Tolls', 0), None),
    ('Other', cat_totals.get('Other', 0) + cat_totals.get('Other Shopping', 0) + cat_totals.get('Vehicle Reg', 0) + cat_totals.get('Apple Store', 0) + cat_totals.get('Shipping', 0) + cat_totals.get('Rideshare', 0) + cat_totals.get('RH Gold', 0), None),
]

total_all = sum(b[1] for b in buckets) + church + mortgage + prop_tax - (mortgage + prop_tax + church)  # avoid double count
# Actually just sum all
total_out = sum(b[1] for b in buckets)

print(f"{'Expense':<42} {'Annual':>10} {'Monthly':>10} {'% Net':>7} {'Note'}")
print("-" * 90)
for name, amt, note in sorted(buckets, key=lambda x: -x[1]):
    if amt < 1: continue
    pct = amt / net * 100
    n = note if note else ''
    flag = ' !!!' if pct > 8 else ' !' if pct > 5 else ''
    print(f"  {name:<40} ${amt:>9,.0f} ${amt/12:>8,.0f}/mo {pct:>5.1f}%{flag} {n}")
print(f"  {'-'*88}")
print(f"  {'TOTAL OUT':<40} ${total_out:>9,.0f} ${total_out/12:>8,.0f}/mo {total_out/net*100:>5.1f}%")
print(f"  {'REMAINING (savings/investments)':<40} ${net-total_out:>+9,.0f} ${(net-total_out)/12:>+8,.0f}/mo {(net-total_out)/net*100:>5.1f}%")
