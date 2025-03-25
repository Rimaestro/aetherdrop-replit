import logging
import os
from app.keep_alive import keep_alive

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_environment():
    """Fungsi untuk memeriksa apakah lingkungan dapat berjalan dengan baik."""
    logger.info("Memeriksa lingkungan...")
    
    # Memeriksa token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN tidak ditemukan. Pastikan Anda telah mengatur Secrets di Replit.")
    else:
        logger.info("TELEGRAM_BOT_TOKEN ditemukan.")
    
    # Memeriksa user ID
    user_id = os.getenv('AUTHORIZED_USER_ID')
    if not user_id:
        logger.warning("AUTHORIZED_USER_ID tidak ditemukan. Pastikan Anda telah mengatur Secrets di Replit.")
    else:
        logger.info("AUTHORIZED_USER_ID ditemukan.")
    
    logger.info("Pemeriksaan lingkungan selesai. Bot siap dijalankan!")

if __name__ == "__main__":
    logger.info("Memulai program...")
    
    # Jalankan server Flask di thread terpisah untuk mencegah Replit sleep
    keep_alive()
    
    # Periksa lingkungan
    check_environment()
    
    logger.info("Program berjalan dengan baik! Lingkungan Replit siap untuk bot Telegram.")
    logger.info("Untuk menjalankan bot penuh, hapus kode pengujian ini dan kembalikan ke kode bot asli.") 