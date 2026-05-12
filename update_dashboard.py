import os
import json
import yfinance as yf
from flask import Flask, render_template_string, request, jsonify
from fyers_apiv3 import fyersModel
import google.generativeai as genai
from pydantic import BaseModel

app = Flask(__name__)

# 1. System Secure Authentication Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FYERS_APP_ID = os.getenv("FYERS_APP_ID")
FYERS_SECRET_KEY = os.getenv("FYERS_SECRET_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Global broker instance (Instantiated dynamically via morning login)
fyers = None
AUTOTRADE_STATE = False

class ScalpSignalSchema(BaseModel):
    signal: str  # BUY, SELL, or HOLD
    target_price: float
    stoploss_price: float
    confidence_score: int  # Percentage 1-100
    execution_reasoning: str

# 2. Premium Dark Trading Desk UI
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ AlphaQuant Pro // Algo Execution Desk</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'JetBrains Mono', monospace; }</style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between selection:bg-emerald-500/30">
    <div class="container mx-auto px-4 py-6 max-w-5xl">
        
        <header class="border-b border-slate-800 pb-5 mb-8 flex justify-between items-center">
            <div>
                <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    <h1 class="text-xl font-bold tracking-wider text-slate-200">ALPHAQUANT // HFT EXECUTION CORE</h1>
                </div>
                <p class="text-slate-500 text-xs mt-1">Real-Time Cloud Deployment Engine</p>
            </div>
            <div id="connectionStatus" class="text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-md text-emerald-400 font-bold">
                CORE SYSTEM ONLINE
            </div>
        </header>

        <main class="space-y-6">
            <div class="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-xl">
                <div>
                    <h2 class="text-lg font-bold text-slate-200">MASTER ALGORITHMIC SWITCH</h2>
                    <p class="text-xs text-slate-500 mt-1">When turned on, Gemini live-monitors the ticks and instantly fires orders to FYERS with zero delays.</p>
                </div>
                <button id="masterSwitch" onclick="toggleExecution()" class="w-full md:w-auto px-8 py-3.5 rounded-xl bg-rose-600 font-extrabold text-sm tracking-widest shadow-lg shadow-rose-950/50 hover:bg-rose-500 transition-all duration-200">
                    AUTO-TRADING DISABLED
                </button>
            </div>

            <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-6">
                <h3 class="text-xs font-bold text-emerald-400 uppercase tracking-widest mb-4">🤖 LIVE AI SCALPER ORDERS</h3>
                <div id="terminalLog" class="bg-slate-950 rounded-xl p-4 border border-slate-800/80 h-48 overflow-y-auto text-xs text-slate-400 space-y-2 font-mono">
                    <p class="text-slate-600">// Engine initialized. Standing by for real-time tick integration...</p>
                </div>
            </div>
        </main>

        <footer class="text-center text-xs text-slate-700 mt-12 pt-4 border-t border-slate-900">
            PROPRIETARY ARCHITECTURE // PIPED API CONNECTIONS SECURED OUTSIDE PUBLIC SPACE
        </footer>
    </div>

    <script>
        let running = false;
        function toggleExecution() {
            running = !running;
            const btn = document.getElementById('masterSwitch');
            if(running) {
                btn.className = "w-full md:w-auto px-8 py-3.5 rounded-xl bg-emerald-500 text-slate-950 font-black text-sm tracking-widest shadow-lg shadow-emerald-500/20 hover:bg-emerald-400 transition-all duration-200";
                btn.innerText = "AUTO-TRADING: ENABLED";
                addLog("CRITICAL: Master switch activated. AI Engine now routing predictive live scalps.");
            } else {
                btn.className = "w-full md:w-auto px-8 py-3.5 rounded-xl bg-rose-600 font-extrabold text-sm tracking-widest shadow-lg shadow-rose-950/50 hover:bg-rose-500 transition-all duration-200";
                btn.innerText = "AUTO-TRADING DISABLED";
                addLog("SYSTEM: Auto-trading halted safely.");
            }
            fetch('/api/toggle_bot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ status: running })
            });
        }

        function addLog(text) {
            const log = document.getElementById('terminalLog');
            const p = document.createElement('p');
            p.innerHTML = `> \${text}`;
            log.appendChild(p);
            log.scrollTop = log.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_DASHBOARD)

# 3. Morning Handshake: Convert Auth Code into Daily Access Token
@app.route('/callback')
def fyers_callback():
    """Captures morning auth_code from the URL and exchanges it for a live daily session token."""
    global fyers
    auth_code = request.args.get('auth_code')
    if not auth_code:
        return "Authentication error: Missing 'auth_code' URL parameter from FYERS verification process.", 400
        
    try:
        # Build the handshake parameters using Render's environment variables
        session = fyersModel.SessionModel(
            client_id=FYERS_APP_ID,
            secret_key=FYERS_SECRET_KEY,
            redirect_uri="http://127.0.0.1:5000/callback",
            response_type="code",
            grant_type="authorization_code"
        )
        session.set_token(auth_code)
        response = session.generate_token()
        
        access_token = response.get("access_token")
        if access_token:
            # Instantiate the broker entity globally for today's trading window
            fyers = fyersModel.FyersModel(client_id=FYERS_APP_ID, is_async=False, token=access_token)
            return "🎯 ALGO INITIALIZED! Your trading app is now fully authorized for today's session. You can safely close this tab and return to your main dashboard URL."
        else:
            return f"Token conversion failed. Response received: {response}", 400
    except Exception as e:
        return f"Authentication loop exception: {str(e)}", 500

@app.route('/api/toggle_bot', methods=['POST'])
def toggle_bot():
    global AUTOTRADE_STATE
    data = request.get_json() or {}
    AUTOTRADE_STATE = data.get("status", False)
    return jsonify({"status": AUTOTRADE_STATE})

# 4. High-Frequency Tick Entry/Exit Processing Pipeline
@app.route('/api/process_tick', methods=['POST'])
def process_tick():
    """Receives streaming data ticks and instantly triggers the predictive execution frame."""
    global AUTOTRADE_STATE, fyers
    if not AUTOTRADE_STATE:
        return jsonify({"status": "disabled", "reason": "Master engine switch is off."})

    data = request.get_json() or {}
    spot_price = data.get("price")
    symbol = data.get("symbol", "NSE:NIFTY50-INDEX")
    history_context = data.get("history", [])

    prompt = f"""
    You are an active, real-time automated quantitative scaling model tracking order flow imbalances on the National Stock Exchange (NSE).
    Instrument Spot: {symbol} -> Price Level: {spot_price}
    Recent Multi-Tick Micro Structure: {history_context}

    Evaluate instant breakout velocity. If a high-probability trade location is recognized, fire an entry signal instantly.
    """
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="You are a high-frequency algorithmic derivatives execution system. Make rapid, calculated trading decisions based on short-term price levels."
        )
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=ScalpSignalSchema,
                temperature=0.1
            )
        )
        
        decision = json.loads(response.text)
        signal = decision.get("signal", "HOLD").upper()

        # Place live trade instantly if broker configuration is active and signal hits BUY/SELL
        if fyers and signal in ["BUY", "SELL"]:
            order_payload = {
                "symbol": "NSE:NIFTY26MAY23400CE",  # Can be mapped to a dynamic options strike selector later
                "qty": 75,  # 1 Lot Nifty
                "type": 2,  # Market order guarantees instant zero-delay execution
                "side": 1 if signal == "BUY" else -1,
                "productType": "MARGIN",
                "limitPrice": 0,
                "stopPrice": 0,
                "validity": "DAY"
            }
            fyers.place_order(data=order_payload)
            
        return jsonify(decision)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
