from fyers_apiv3 import fyersModel

# 1. System Secure Authentication Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FYERS_APP_ID = os.getenv("FYERS_APP_ID")
FYERS_SECRET_KEY = os.getenv("FYERS_SECRET_KEY")  # Put your app secret key in Render variables

genai.configure(api_key=GEMINI_API_KEY)

# Active session instance container
fyers = None

@app.route('/callback')
def fyers_callback():
    """Captures the morning auth_code from the URL and converts it into a live daily token."""
    global fyers
    auth_code = request.args.get('auth_code')
    if not auth_code:
        return "Authentication error: No auth_code received from FYERS.", 400
        
    try:
        # Create a session model handshake
        session = fyersModel.SessionModel(
            client_id=FYERS_APP_ID,
            secret_key=FYERS_SECRET_KEY,
            redirect_uri="http://127.0.0.1:5000/callback",
            response_type="code",
            grant_type="authorization_code"
        )
        session.set_token(auth_code)
        response = session.generate_token()
        
        # Capture the ultimate daily execution token
        access_token = response.get("access_token")
        if access_token:
            fyers = fyersModel.FyersModel(client_id=FYERS_APP_ID, is_async=False, token=access_token)
            return "🎯 ALGO INITIALIZED! Your trading app is now fully authorized for today's session. You can safely close this tab and go to your main dashboard link."
        else:
            return f"Token conversion failed: {response}", 400
    except Exception as e:
        return f"Authentication exception: {str(e)}", 500
