# 挨拶を各国の言語に変えて返すアプリ。QRコードを読み込んだデバイスのブラウザ情報とIPアドレスからの読み込みへ対応
# 起動コマンド　flask run --host=0.0.0.0 --port=5001
# サーバーのバックグランドでの起動コマンド　nohup python app.py > output.log 2>&1 &

# ngrokを使用する場合
# 1. brew install ngrok
# 2. ngrok config add-authtoken あなたの認証トークン
# 3. ngrok http 5001
# 4. http://127.0.0.1:4040 へアクセス（うまくいったら表示される）
# 5. Ctrl+C で終了

from flask import Flask, render_template, request, jsonify
from waitress import serve
import geoip2.database as geodb
import qrcode
import base64
import redis
from io import BytesIO
import uuid

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0)  # この行を追加

# GeoIP2のデータベースを読み込み
reader = geodb.Reader(
    "GeoLite2-Country.mmdb"
    )

# 対応言語のリスト
LANGUAGES = {
    'en': 'Hello, World!', # イギリス（イングランド）、アメリカ
    'ja': 'ハロー、ワールド！', # 日本
    'es': '¡Hola Mundo!', # スペイン、メキシコ
    'fr': 'Bonjour le monde!', # フランス
    'de': 'Hallo Welt!', # ドイツ
    'it': 'Ciao mondo!', # イタリア
    'zh': '你好，世界！', # 中国
    'ko': '안녕하세요, 세계!', # 韓国
    'ru': 'Привет, мир!', # ロシア
    'pt': 'Olá, mundo!', # ポルトガル、ブラジル
    'th': 'สวัสดี, โลก!', # タイ
    'vi': 'Xin chào, thế giới!' # ベトナム
}

# 国コードと言語コードのマッピング（簡略化のため一部の国のみ）
COUNTRY_LANG = {
    'US': 'en', 'GB': 'en', 'JP': 'ja', 'ES': 'es', 'FR': 'fr', 
    'DE': 'de', 'IT': 'it', 'CN': 'zh', 'KR': 'ko', 'RU': 'ru',
    'BR': 'pt', 'PT': 'pt', 'TH': 'th', 'VN': 'vi'
}

def get_preferred_language(request):
    lang = request.args.get('lang')
    if lang and lang in LANGUAGES:
        return lang
    else:
        return request.accept_languages.best_match(LANGUAGES.keys())

def get_country_from_ip(reader, ip_address):
    try:
        response = reader.country(ip_address)
        return response.country.name, response.country.iso_code
    except:
        return "Unknown", "UN"

def get_greeting_from_country_code(country_code):
    lang = COUNTRY_LANG.get(country_code, 'en')  # デフォルトは英語
    return LANGUAGES.get(lang, LANGUAGES['en'])

def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@app.route('/')
def index():
    unique_id = str(uuid.uuid4())
    if request.headers.getlist("X-Forwarded-For"):
        ip_address = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_address = request.remote_addr

    country_name, country_code = get_country_from_ip(reader, ip_address)    
    browser_lang = get_preferred_language(request)
    browser_greeting = LANGUAGES.get(browser_lang, LANGUAGES['en'])
    ip_greeting = get_greeting_from_country_code(country_code)
    qr_data = generate_qr_code(request.url_root + f"greet/{unique_id}")

    return render_template(
        'index.html', 
        ip_address=ip_address, 
        country=country_name,
        browser_greeting=browser_greeting,
        ip_greeting=ip_greeting,
        languages=LANGUAGES, 
        current_lang=browser_lang,
        qr_data=qr_data,
        unique_id=unique_id
    )

@app.route("/get_ip", methods=["GET"])
def get_ip():
    return jsonify({'ip': request.remote_addr}), 200

@app.route('/update_language/<unique_id>')
def update_language(unique_id):
    greeting_type = request.args.get('type', 'browser')
    
    if greeting_type == 'browser':
        # スマートフォンのブラウザ言語を使用
        stored_browser_language = r.get(f"{unique_id}_browser_language")
        if stored_browser_language:
            language = stored_browser_language.decode('utf-8')
        else:
            language = 'en'
    elif greeting_type == 'ip':
        # IPアドレスベースの言語を使用
        stored_language = r.get(f"{unique_id}_language")
        if stored_language:
            language = stored_language.decode('utf-8')
        else:
            language = 'en'
    
    greeting = LANGUAGES.get(language, LANGUAGES['en'])
    
    stored_ip = r.get(f"{unique_id}_ip")
    stored_country = r.get(f"{unique_id}_country")
    
    return jsonify({
        'greeting': greeting, 
        'language': language,
        'ip': stored_ip.decode('utf-8') if stored_ip else 'Not scanned yet',
        'country': stored_country.decode('utf-8') if stored_country else 'Unknown'
    })


@app.route('/greet/<unique_id>')
def greet(unique_id):
    # スマートフォンの情報を取得
    if request.headers.getlist("X-Forwarded-For"):
        ip_address = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_address = request.remote_addr

    # IPアドレスから国を取得
    country_name, country_code = get_country_from_ip(reader, ip_address)    
    # スマートフォンのブラウザ言語を取得
    browser_language = get_preferred_language(request)
    
    # Redisに情報を保存
    r.set(f"{unique_id}_ip", ip_address)
    r.set(f"{unique_id}_country", country_name)
    r.set(f"{unique_id}_language", COUNTRY_LANG.get(country_code, 'en'))
    r.set(f"{unique_id}_browser_language", browser_language)

    # 現在のモードを取得（デフォルトは'browser'）
    current_mode = r.get(f"{unique_id}_mode")
    if current_mode:
        current_mode = current_mode.decode('utf-8')
    else:
        current_mode = 'browser'

    # モードに応じて言語を選択
    if current_mode == 'browser':
        language = browser_language
    else:  # ip mode
        language = COUNTRY_LANG.get(country_code, 'en')
    
    greeting = LANGUAGES.get(language, LANGUAGES['en'])
    
    return render_template('greeting.html', 
                         greeting=greeting, 
                         unique_id=unique_id,
                         ip_address=ip_address,
                         country=country_name,
                         mode=current_mode)  # モードも渡す

@app.route('/save_mode/<unique_id>', methods=['POST'])
def save_mode(unique_id):
    mode = request.form.get('mode', 'ip')
    r.set(f"{unique_id}_mode", mode)
    return jsonify({'status': 'success'})

@app.route('/get_mode/<unique_id>')
def get_mode(unique_id):
    mode = r.get(f"{unique_id}_mode")
    if mode:
        mode = mode.decode('utf-8')
    else:
        mode = 'ip'
    return jsonify({'mode': mode})

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5001)