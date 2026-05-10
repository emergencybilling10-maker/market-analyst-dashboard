import os
import yfinance as yf
import google.generativeai as genai

# 1. Setup Gemini AI
# The API key will be pulled securely from GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_market_analysis():
    # 2. Fetch Live Market Data (Nifty 50 and Bitcoin)
    nifty = yf.Ticker("^NSEI").history(period="7d")
    btc = yf.Ticker("BTC-USD").history(period="7d")
    
    nifty_close = round(nifty['Close'].iloc[-1], 2)
    nifty_change = round(((nifty['Close'].iloc[-1] - nifty['Close'].iloc[-2]) / nifty['Close'].iloc[-2]) * 100, 2)
    
    btc_close = round(btc['Close'].iloc[-1], 2)
    btc_change = round(((btc['Close'].iloc[-1] - btc['Close'].iloc[-2]) / btc['Close'].iloc[-2]) * 100, 2)

    # Determine dynamic styling classes to prevent f-string bracket errors
    nifty_class = 'bg-emerald-950 text-emerald-400' if nifty_change >= 0 else 'bg-rose-950 text-rose-400'
    btc_class = 'bg-emerald-950 text-emerald-400' if btc_change >= 0 else 'bg-rose-950 text-rose-400'

    # 3. Prompt the AI for "Supercomputed" Market Insights
    prompt = f"""
    You are an elite, high-frequency quantitative market analyst. 
    Analyze the current market snapshot and provide a concise, sharp outlook (bullish/bearish/neutral) and 2-3 key takeaways.
    
    Current Data:
    - Nifty 50 Index: {nifty_close} ({nifty_change}% change today)
    - Bitcoin (BTC/USD): ${btc_close} ({btc_change}% change today)
    
    Format your response in clean HTML bullet points. Do not include markdown wrappers like ```html in your output. Just output the list elements.
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        ai_insights = response.text
    except Exception as e:
        ai_insights = f"<li>Error generating AI analysis: {str(e)}</li>"

    # 4. Generate the HTML Page
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live AI Market Analyst</title>
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen flex flex-col justify-between">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <header class="border-b border-slate-700 pb-4 mb-8">
            <h1 class="text-3xl font-bold tracking-tight text-emerald-400">🧠 AI Market Intelligence Dashboard</h1>
            <p class="text-slate-400 text-sm mt-1">Automated Analysis • Powered by GitHub Actions & Gemini</p>
        </header>

        <main class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-slate-800 p-6 rounded-lg border border-slate-700">
                    <h2 class="text-xl font-semibold text-slate-300">Nifty 50</h2>
                    <p class="text-4xl font-extrabold mt-2">{nifty_close}</p>
                    <span class="inline-block mt-2 px-2 py-1 text-xs rounded font-bold {nifty_class}">
                        {"+" if nifty_change >= 0 else ""}{nifty_change}%
                    </span>
                </div>
                
                <div class="bg-slate-800 p-6 rounded-lg border border-slate-700">
                    <h2 class="text-xl font-semibold text-slate-300">Bitcoin</h2>
                    <p class="text-4xl font-extrabold mt-2">${btc_close:,}</p>
                    <span class="inline-block mt-2 px-2 py-1 text-xs rounded font-bold {btc_class}">
                        {"+" if btc_change >= 0 else ""}{btc_change}%
                    </span>
                </div>
            </div>

            <div class="bg-slate-800 p-6 rounded-lg border border-emerald-500/30 shadow-lg">
                <h2 class="text-xl font-semibold text-emerald-400 mb-4 flex items-center gap-2">
                    ⚡ Live AI Strategist Insights
                </h2>
                <ul class="space-y-3 text-slate-300 list-disc pl-5">
                    {ai_insights}
                </ul>
            </div>
        </main>

        <footer class="text-center text-xs text-slate-500 mt-12 pt-4 border-t border-slate-800">
            Last updated automatically via GitHub Runner.
        </footer>
    </div>
</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    get_market_analysis()
