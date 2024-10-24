# Multilingual Greeting QR

A Flask-based web application that displays greetings in multiple languages based on browser settings and IP geolocation. It includes QR code functionality for mobile device integration.

## Features

- Supports 12 different languages including English, Japanese, Spanish, etc.
- Automatically detects user's country based on IP address
- Recognizes browser language settings
- Generates QR codes for easy mobile access
- Switches between browser language and IP-based language modes
- Real-time greeting updates

## Requirements

- Python 3.7+
- Redis
- Flask
- GeoIP2 database
- NGrok (optional, for public access)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multilingual-greeting-qr.git
cd multilingual-greeting-qr
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up Redis:
```bash
# For MacOS
brew install redis
# For Ubuntu
sudo apt-get install redis-server
```

4. Download GeoLite2 Country database and place it in the project root directory.

## Usage

1. Start Redis server:
```bash
redis-server
```

2. Run the application:
```bash
flask run --host=0.0.0.0 --port=5001
```

For background server operation:
```bash
nohup python app.py > output.log 2>&1 &
```

### Using NGrok (Optional)

1. Install NGrok:
```bash
brew install ngrok  # For MacOS
```

2. Configure NGrok:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

3. Start NGrok tunnel:
```bash
ngrok http 5001
```

4. Access NGrok interface at: http://127.0.0.1:4040

## License

MIT

---

# マルチリンガル・グリーティングQR

ブラウザ設定とIP位置情報に基づいて多言語で挨拶を表示するFlaskベースのWebアプリケーションです。モバイルデバイス連携のためのQRコード機能も搭載しています。

## 機能

- 英語、日本語、スペイン語など12言語に対応
- IPアドレスに基づく国の自動検出
- ブラウザの言語設定の認識
- モバイルアクセス用QRコード生成
- ブラウザ言語モードとIP基準言語モードの切り替え
- リアルタイムでの挨拶更新

## 必要要件

- Python 3.7以上
- Redis
- Flask
- GeoIP2データベース
- NGrok（オプション、パブリックアクセス用）

## インストール方法

1. リポジトリのクローン:
```bash
git clone https://github.com/yourusername/multilingual-greeting-qr.git
cd multilingual-greeting-qr
```

2. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
```

3. Redisのセットアップ:
```bash
# MacOSの場合
brew install redis
# Ubuntuの場合
sudo apt-get install redis-server
```

4. GeoLite2 Countryデータベースをダウンロードし、プロジェクトのルートディレクトリに配置してください。

## 使用方法

1. Redisサーバーの起動:
```bash
redis-server
```

2. アプリケーションの実行:
```bash
flask run --host=0.0.0.0 --port=5001
```

バックグラウンドでサーバーを実行する場合:
```bash
nohup python app.py > output.log 2>&1 &
```

### NGrokの使用（オプション）

1. NGrokのインストール:
```bash
brew install ngrok  # MacOSの場合
```

2. NGrokの設定:
```bash
ngrok config add-authtoken あなたの認証トークン
```

3. NGrokトンネルの開始:
```bash
ngrok http 5001
```

4. NGrokインターフェースへのアクセス: http://127.0.0.1:4040

## ライセンス

MIT
