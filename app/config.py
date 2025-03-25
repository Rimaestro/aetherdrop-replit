import os
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
# Di Replit, gunakan Secrets untuk menyimpan variabel sensitif
load_dotenv()

# Token bot dari BotFather Telegram
# Di Replit, tambahkan ini di Secrets dengan nama TELEGRAM_BOT_TOKEN
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Konfigurasi database
DB_NAME = 'airdrop.db'

# ID pengguna yang diizinkan menggunakan bot
# Di Replit, tambahkan ini di Secrets dengan nama AUTHORIZED_USER_ID
AUTHORIZED_USER_ID = int(os.getenv('AUTHORIZED_USER_ID', 0)) 