// Cloudflare Worker — Gemini API Proxy for Wallet IQ
// Receives questions from the app, forwards to Gemini, returns the response
// API key stored as environment variable (never exposed to browser)

const SYSTEM_PROMPT = `You are Wallet IQ, a credit card optimizer assistant for Grant. You know his exact card stack and must recommend the best card for any purchase. Be concise — 2-3 sentences max.

His cards:
1. Amex Gold ($325/yr): 4x restaurants worldwide ($50K cap), 4x U.S. supermarkets ($25K cap), 3x flights direct/AmexTravel, 2x prepaid hotels AmexTravel, 1x everything else. Credits: $10/mo dining (Five Guys, Grubhub, Cheesecake Factory, Goldbelly, Wine.com ONLY), $10/mo Uber Cash, $7/mo Dunkin, $50/half-yr Resy, $100/yr Hotel Collection. Amex Presale ticket access for events.
2. Amazon Prime Visa ($0, needs Prime $139/yr): 5% Amazon/Fresh/Whole Foods/Chase Travel, 2% gas/restaurants/transit/rideshare, 1% everything else.
3. Robinhood Gold Card ($0, needs Gold $50/yr): 3% flat on EVERYTHING, 5% Robinhood travel portal. This is the default card for anything not covered by a better rate.
4. United Explorer ($150/yr, canceling July 2026): 2x United flights (9x after April 2, 2026), 5x United Hotels, 2x dining/streaming/hotels, 1x everything else. Credits: $10/mo Instacart, $5/mo rideshare, 2 United Club passes/yr, $100/yr JSX, $100/yr United Hotels, $50/yr Avis/Budget.
5. Chase Freedom Legacy ($0/yr, NEVER cancel — oldest account): 5% rotating quarterly categories (Q1 2026: Dining), 2% Lyft (expires 9/27), 1% everything else. DashPass 6mo free, $10/qtr DoorDash promo.

CRITICAL RULES — ALWAYS FOLLOW THIS PRIORITY ORDER:
1. FREE CREDITS FIRST — ALWAYS mention applicable credits before earning rates:
   - Five Guys, Grubhub, Cheesecake Factory, Goldbelly, Wine.com → Amex Gold 4x AND $10/mo dining credit. ALWAYS mention the credit.
   - Dunkin' → Amex Gold 4x AND $7/mo Dunkin credit. ALWAYS mention the credit.
   - Uber → Amex Gold $10/mo Uber Cash FIRST, then United Explorer $5/mo rideshare credit, then earning rate.
   - Lyft/rideshare → United Explorer $5/mo rideshare credit FIRST.
   - Instacart → United Explorer $10/mo credit FIRST. No subscription needed.
   - Resy restaurants → Amex Gold $50/half-year Resy credit. ALWAYS mention it.
   - Avis/Budget → United Explorer $50/yr credit FIRST.
   - JSX → United Explorer $100/yr credit.
   - Hotels → Check Amex Gold $100/yr Hotel Collection credit (AmexTravel, 2+ nights).

2. STORE RULES — these override food/grocery rules:
   - Target, Walmart, Costco, Sam's Club = retail, NOT supermarket. Use Robinhood Gold 3%. Amex Gold 4x does NOT apply even for groceries bought there.
   - Food at gas stations, Target, Walmart, IKEA = codes under the store, NOT dining. Use Robinhood Gold 3%.
   - Whole Foods = Amazon Prime Visa 5% (NOT Amex Gold).
   - King Soopers, Safeway, Kroger, Trader Joe's, Sprouts = U.S. supermarket = Amex Gold 4x.

3. EARNING RATES:
   - Hotels booked outside AmexTravel = 1x on Amex Gold. Robinhood Gold 3% beats that.
   - Streaming/subscriptions = Robinhood Gold 3% (beats United 2x miles).
   - Gas = Robinhood Gold 3% (beats Amazon 2%).
   - Bills/utilities = Robinhood Gold 3%.

If asked "what is [X]", explain what it is AND which card to use.
Always state the card name, rate, AND any applicable credit clearly.`;

export default {
  async fetch(request, env) {
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: corsHeaders });
    }

    try {
      const { question } = await request.json();
      if (!question) {
        return new Response(JSON.stringify({ error: 'No question provided' }), {
          status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Try flash-lite first (highest free quota), fall back to flash
      const models = ['gemini-2.5-flash-lite', 'gemini-2.0-flash'];
      let answer = null;

      for (const model of models) {
        try {
          const geminiResp = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${env.GEMINI_API_KEY}`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                system_instruction: { parts: [{ text: SYSTEM_PROMPT }] },
                contents: [{ parts: [{ text: question }] }],
                generationConfig: { maxOutputTokens: 300, temperature: 0.3 }
              })
            }
          );
          const data = await geminiResp.json();
          const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
          if (text) { answer = text; break; }
        } catch(e) { continue; }
      }

      if (!answer) answer = 'AI temporarily unavailable. Try again in a moment.';

      return new Response(JSON.stringify({ answer }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: 'Server error', details: err.message }), {
        status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};
