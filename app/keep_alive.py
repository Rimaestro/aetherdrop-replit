from flask import Flask
from threading import Thread

# Membuat aplikasi Flask
app = Flask(__name__)

# Definisikan route utama
@app.route('/')
def home():
    return "Bot AetherDrop sedang berjalan! Bot ini akan tetap aktif selama website ini di-ping."

# Fungsi untuk menjalankan server
def run():
    app.run(host='0.0.0.0', port=8080)

# Fungsi untuk memulai server di thread terpisah
def keep_alive():
    t = Thread(target=run)
    t.start() 