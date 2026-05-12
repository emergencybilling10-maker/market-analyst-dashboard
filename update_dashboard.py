import os
import json
import yfinance as yf
import google.generativeai as genai
from pydantic import BaseModel  # Fixed import for structured outputs

# 1. Setup Institutional Grade Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("CRITICAL ERROR: GEMINI_API_KEY environment variable is missing.")

genai.configure(api_key=GEMINI_API_KEY)

# Define strict JSON schema using native Pydantic
class MarketInsightsSchema(BaseModel):
    volatility_insight: str
    options_chain_insight: str
    actionable_outlook: str

def fetch_ticker_data(symbol: str, period: str = "7d"):
    """Safely fetches ticker data and handles market close/empty df exceptions."""
    try:
        df = yf.Ticker(symbol).history(period=period)
        if df.empty or len(df) < 2:
            return None
        return df
    except Exception:
        return None

def get_market_analysis():
    # 2. Fetch Live Market Data with Fallbacks
    nifty_df = fetch_ticker_data("^NSEI")
    btc_df = fetch_ticker_data("BTC-USD")
    
    # Handle missing Nifty data edge-cases gracefully
    if nifty_df is not None:
        nifty_close = round(nifty_df['Close'].iloc[-1], 2)
        nifty_change = round(((nifty_df['Close'].iloc[-1] - nifty_df['Close'].iloc[-2]) / nifty_df['Close'].iloc[-2]) * 100, 2)
        nifty_high = round(nifty_df['High'].iloc[-1], 2)
        nifty_low = round(nifty_df['Low'].iloc[-1], 2)
    else:
        nifty_close, nifty_change, nifty_high, nifty_low = 0.0, 0.0, 0.0, 0.0

    if btc_df is not None:
        btc_close = round(btc_df['Close'].iloc[-1], 2)
        btc_change = round(((btc_df['Close'].iloc[-1] - btc_df['Close'].iloc[-2]) / btc_df['Close'].iloc[-2]) * 100, 2)
    else:
        btc_close, btc_change = 0.0, 0.0

    # Dynamic Styling Classes (Extracted out to prevent HTML f-string template crashes)
    nifty_color = 'text-emerald-400' if nifty_change >= 0 else 'text-rose-500'
    nifty_bg = 'bg-emerald-950/20 border-emerald-500/30' if nifty_change >= 0 else 'bg-rose-950/20 border-rose-500/30'
    nifty_text_badge = 'text-emerald-400 bg-emerald-950/80' if nifty_change >= 0 else 'text-rose-400 bg-rose-950/80'

    btc_color = 'text-emerald-400' if btc_change >= 0 else 'text-rose-500'
    btc_bg = 'bg-emerald-950/20 border-emerald-500/30' if btc_change >= 0 else 'bg-rose-950/20 border-rose-500/30'
    btc_text_badge = 'text-emerald-400 bg-emerald-950/80' if btc_change >= 0 else 'text-rose-400 bg-rose-950/80'

    # 3. Dynamic Structured Querying to Gemini API
    prompt = f"""
    Analyze this real-time snapshot:
    - Nifty 50 Spot: {nifty_close} (Day High: {nifty_high}, Day Low: {nifty_low}, Change: {nifty_change}%)
    - Global Risk Sentiment Indicator (Bitcoin): ${btc_close} ({btc_change}%)

    Deliver expert analysis filling all schema requirements perfectly.
    """
    
    try:
        # Initializing production-tier engine with system contexts
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=(
                "You are an elite institutional Derivatives & F&O Strategist specializing in the Indian National Stock Exchange (NSE). "
                "Provide deep quantitative insights contextually optimized for intraday, momentum, and options structure analysis."
            )
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=MarketInsightsSchema,
                temperature=0.2
            )
        )
        
        insights_data = json.loads(response.text)
        
        # Build HTML components natively to protect the web layouts structure
        ai_insights_html = f"""
        <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow-md">
            <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider">PRICING STABILITY & VOLATILITY EXPECTATION</h3>
            <p class="text-slate-200 mt-2 text-sm leading-relaxed">{insights_data.get('volatility_insight', '')}</p>
        </div>
        <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow-md">
            <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider">OPTIONS CHAIN STRATEGY & KEY LEVELS</h3>
            <p class="text-slate-200 mt-2 text-sm leading-relaxed">{insights_data.get('options_chain_insight', '')}</p>
        </div>
        <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow-md">
            <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider">DERIVATIVES ACTIONABLE OUTLOOK</h3>
            <p class="text-slate-200 mt-2 text-sm leading-relaxed">{insights_data.get('actionable_outlook', '')}</p>
        </div>
        """
    except Exception as e:
        ai_insights_html = f"""
        <div class="bg-rose-950/40 p-5 rounded-xl border border-rose-500/30 col-span-full">
            <h3 class="text-sm font-semibold text-rose-400 uppercase">System Error</h3>
            <p class="text-slate-300 mt-2 text-sm">Failed to stream strategist intelligence: {str(e)}</p>
        </div>
        """

    # 4. Generate Premium Tailwind Terminal Dashboard UI
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ AlphaQuant // F&O Market Terminal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'JetBrains Mono', monospace; }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between selection:bg-emerald-500/30">
    <div class="container mx-auto px-4 py-6 max-w-6xl">
        
        <header class="border-b border-slate-800 pb-5 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <h1 class="text-xl font-extrabold tracking-wider text-slate-200 uppercase">ALPHAQUANT // DERIVATIVES DESK</h1>
                </div>
                <p class="text-slate-500 text-xs mt-1">Automated AI Analytics • Live Execution Data</p>
            </div>
            <div class="text-right">
                <span class="text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-md text-slate-400 font-semibold">
                    SYSTEM STATUS: ACTIVE RUNNER
                </span>
            </div>
        </header>

        <main class="space-y-6">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div class="{nifty_bg} p-6 rounded-2xl border backdrop-blur-md shadow-xl transition hover:border-slate-600">
                    <div class="flex justify-between items-start">
                        <span class="text-xs font-bold text-slate-400 uppercase tracking-widest bg-slate-900/80 px-2.5 py-1 rounded">INDEX // NIFTY 50 SPOT</span>
                        <span class="text-xs font-black px-2 py-0.5 rounded {nifty_text_badge}">
                            {"+" if nifty_change >= 0 else ""}{nifty_change}%
                        </span>
                    </div>
                    <p class="text-5xl font-black mt-4 tracking-tight {nifty_color}">{nifty_close}</p>
                    <div class="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-slate-800/60 text-xs text-slate-400">
                        <div>DAY HIGH: <span class="text-slate-200 font-semibold">{nifty_high}</span></div>
                        <div>DAY LOW: <span class="text-slate-200 font-semibold">{nifty_low}</span></div>
                    </div>
                </div>
                
                <div class="{btc_bg} p-6 rounded-2xl border backdrop-blur-md shadow-xl transition hover:border-slate-600">
                    <div class="flex justify-between items-start">
                        <span class="text-xs font-bold text-slate-400 uppercase tracking-widest bg-slate-900/80 px-2.5 py-1 rounded">MACRO // GLOBAL RISK (BTC)</span>
                        <span class="text-xs font-black px-2 py-0.5 rounded {btc_text_badge}">
                            {"+" if btc_change >= 0 else ""}{btc_change}%
                        </span>
                    </div>
                    <p class="text-5xl font-black mt-4 tracking-tight {btc_color}">${btc_close:,}</p>
                    <div class="mt-4 pt-4 border-t border-slate-800/60 text-xs text-slate-400">
                        ASSET PROFILE: CRYPTO SENTIMENT LEADER
                    </div>
                </div>
            </div>

            <div class="pt-4">
                <h2 class="text-xs font-bold text-emerald-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <span class="inline-block w-1.5 h-3 bg-emerald-500"></span> QUANTITATIVE AI STRATEGIST MATRIX
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {ai_insights_html}
                </div>
            </div>
            
        </main>

        <footer class="text-center text-xs text-slate-600 mt-16 pt-6 border-t border-slate-900">
            SECURE REPOSITORY SYSTEM // GENERATED VIA CRON ACTIONS INTERACTION LOOP // NO LOCAL RESIDENCY REQUIRED
        </footer>
    </div>
</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    get_market_analysis()
