import csv, os, re
from collections import defaultdict

all_transactions = []

# Read all CSVs from Amex Gold
amex_dir = "C:/Users/Exterminator/Downloads/Amex Gold Statements/"
for f in os.listdir(amex_dir):
    if f.endswith('.csv'):
        with open(amex_dir + f, 'r', encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    amt = float(row['Amount'])
                    if amt < 0: continue
                    all_transactions.append({'date': row['Date'], 'desc': row['Description'].strip(), 'amount': amt, 'card': 'Amex Gold'})
                except: pass

# Read PDF statements
import pdfplumber

for card_name, dir_path in [
    ('United Explorer', 'C:/Users/Exterminator/Downloads/United Statements/'),
    ('Amazon Prime Visa', 'C:/Users/Exterminator/Downloads/Amazon Prime Statements/'),
    ('Chase Freedom', 'C:/Users/Exterminator/Downloads/Freedom Statements/')
]:
    for fname in sorted(os.listdir(dir_path)):
        if not fname.endswith('.pdf'): continue
        with pdfplumber.open(dir_path + fname) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ''
                for line in text.split('\n'):
                    m = re.match(r'(\d{2}/\d{2})\s+(.+?)\s+([\d,]+\.\d{2})$', line.strip())
                    if m:
                        desc = m.group(2).strip()
                        if any(skip in desc for skip in ['Payment Thank', 'AUTOMATIC PAYMENT', 'AMAZON MKTPLACE PMTS']): continue
                        try:
                            amt = float(m.group(3).replace(',',''))
                            all_transactions.append({'date': m.group(1), 'desc': desc, 'amount': amt, 'card': card_name})
                        except: pass

# Categorize
def categorize(desc):
    d = desc.upper()
    if any(x in d for x in ['AMAZON','AMZN','ALEXA SKILLS','PRIME*']): return 'Amazon'
    if any(x in d for x in ['KING SOOPERS','WHOLEFDS','WHOLE FOODS','SAFEWAY','SPROUTS','TRADER JOE']): return 'Groceries'
    if any(x in d for x in ['SAMSCLUB','SAMS CLUB','SAMS SCAN']): return "Sam's Club"
    if any(x in d for x in ['SHELL OIL','PHILLIPS 66','CONOCO']): return 'Gas'
    if any(x in d for x in ['GEICO']): return 'Insurance (GEICO)'
    if any(x in d for x in ['CLAUDE','ANTHROPIC','OPENAI','CHATGPT']): return 'AI Subscriptions'
    if any(x in d for x in ['DISH TV RIVER']): return 'Work Cafeteria'
    if any(x in d for x in ['DISH DBS','DISH NTWK','AUTOPAY / DISH']): return 'DISH TV'
    if any(x in d for x in ['SLING']): return 'Sling TV'
    if any(x in d for x in ['APPLE.COM','APPLE STORE']): return 'Apple'
    if any(x in d for x in ['BOOST MOBILE']): return 'Phone (Boost)'
    if any(x in d for x in ['HIGHLANDS RANCH WATER']): return 'Water Bill'
    if any(x in d for x in ['WALMART','WM.COM']): return 'Walmart'
    if any(x in d for x in ['NETFLIX','HULU','SPOTIFY','DISNEY','HBO','PARAMOUNT','PEACOCK']): return 'Streaming'
    if any(x in d for x in ['UNITED 01','UNITED.COM']): return 'United Flights'
    if any(x in d for x in ['DEN PUBLIC PARKING','DENVER AIRPORT']): return 'Airport/Parking'
    if any(x in d for x in ['E 470']): return 'Tolls'
    if any(x in d for x in ['FIVE GUYS','5 GUYS']): return 'Five Guys'
    if 'FLOYD' in d: return 'Haircuts'
    if any(x in d for x in ['CHICK-FIL','POTBELLY','EINSTEIN','VIEWHOUSE','LITTLETON BREWERY','PACIFIC BREEZE','SWEET COW','PORTLAND ROAST','CHIPOTLE','MCDONALDS','SUBWAY','TACO BELL','ROCKY']): return 'Dining Out'
    if any(x in d for x in ['BALL ARENA']): return 'Entertainment'
    if any(x in d for x in ['TARGET']): return 'Target'
    if any(x in d for x in ['USPS']): return 'Shipping'
    if any(x in d for x in ['PAYPAL']): return 'PayPal/Online'
    if any(x in d for x in ['UBER','LYFT']): return 'Rideshare'
    if any(x in d for x in ['SAMS CLUB RENEWAL']): return "Sam's Club Membership"
    if any(x in d for x in ['SHELBY','TAILORED','VIVOBAREFOOT','ELECTRIFY','GLF*MURPHY','NYX']): return 'Shopping/Other'
    if any(x in d for x in ['AMEX DINING','AMEX UBER','CREDIT']): return 'Credits/Adjustments'
    return 'Other: ' + desc[:40]

# Process
categories = defaultdict(lambda: {'total': 0, 'count': 0, 'cards': defaultdict(float)})

for t in all_transactions:
    cat = categorize(t['desc'])
    if cat == 'Credits/Adjustments': continue
    categories[cat]['total'] += t['amount']
    categories[cat]['count'] += 1
    categories[cat]['cards'][t['card']] += t['amount']

# Estimate months (use 15 months of data: Jan 2025 - Mar 2026)
num_months = 15

# Optimal card mapping
optimal_map = {
    'Amazon': 'Amazon Prime (5%)',
    'Groceries': 'Amex Gold (4x)',
    "Sam's Club": 'Robinhood (3%)',
    "Sam's Club Membership": 'Robinhood (3%)',
    'Gas': 'Robinhood (3%)',
    'Insurance (GEICO)': 'Robinhood (3%)',
    'AI Subscriptions': 'Robinhood (3%)',
    'Work Cafeteria': 'Amex Gold (4x)',
    'DISH TV': 'Robinhood (3%)',
    'Sling TV': 'Robinhood (3%)',
    'Apple': 'Robinhood (3%)',
    'Phone (Boost)': 'Robinhood (3%)',
    'Water Bill': 'Robinhood (3%)',
    'Walmart': 'Robinhood (3%)',
    'Streaming': 'Robinhood (3%)',
    'United Flights': 'United Explorer (2x)',
    'Airport/Parking': 'Robinhood (3%)',
    'Tolls': 'Robinhood (3%)',
    'Five Guys': 'Amex Gold (4x+credit)',
    'Dining Out': 'Amex Gold (4x)',
    'Haircuts': 'Amex Gold (4x)',
    'Entertainment': 'Robinhood (3%)',
    'Target': 'Robinhood (3%)',
    'Shipping': 'Robinhood (3%)',
    'PayPal/Online': 'Robinhood (3%)',
    'Rideshare': 'Uber Cash first',
    'Shopping/Other': 'Robinhood (3%)',
}

print(f"Total transactions: {len(all_transactions)}")
print(f"Data span: ~{num_months} months")
print(f"\n{'Category':<25} {'Total':>10} {'Mo Avg':>10} {'Primary Card':<22} {'Optimal Card':<22}")
print("-" * 95)

for cat, data in sorted(categories.items(), key=lambda x: -x[1]['total']):
    total = data['total']
    monthly = total / num_months
    primary_card = max(data['cards'].items(), key=lambda x: x[1])[0]
    optimal = optimal_map.get(cat, 'Robinhood (3%)')
    wrong = '*' if primary_card.split()[0] not in optimal else ' '
    print(f"{wrong}{cat:<24} ${total:>9,.0f} ${monthly:>8,.0f}/mo  {primary_card:<22} {optimal:<22}")

grand = sum(d['total'] for d in categories.values())
print(f"\n {'TOTAL':<24} ${grand:>9,.0f} ${grand/num_months:>8,.0f}/mo")
print(f"\n* = currently using wrong card")
