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

CRITICAL RULES:
- Target, Walmart, Costco, Sam's Club = retail, NOT supermarket. Use Robinhood Gold 3%. Amex Gold 4x does NOT apply.
- Whole Foods = Amazon Prime Visa 5% (NOT Amex Gold)
- King Soopers, Safeway, Kroger = U.S. supermarket = Amex Gold 4x
- Hotels booked outside AmexTravel = 1x on Amex Gold. Robinhood Gold 3% beats that.
- Always recommend using free credits/perks BEFORE earning rates (e.g. Uber Cash before rideshare rate)
- Streaming = Robinhood Gold 3% (beats United 2x)
- Gas = Robinhood Gold 3% (beats Amazon 2%)

If asked "what is [X]", explain what it is AND which card to use.
Always state the card name and rate clearly.`;

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

      const geminiResp = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=${env.GEMINI_API_KEY}`,
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
      const answer = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'Sorry, I couldn\'t process that question. Try rephrasing.';

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
