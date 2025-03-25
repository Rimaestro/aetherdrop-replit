import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ConversationHandler, ContextTypes
)

# Import dari package app
from app import database
from app.config import TOKEN
from app.handlers import (
    start_command, help_command, handle_forwarded_message,
    list_airdrops, search_command, button_callback, handle_notes_message
)
from app.keep_alive import keep_alive

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Fungsi utama untuk menjalankan bot."""
    # Membuat tabel database jika belum ada
    database.create_tables()
    
    # Inisialisasi aplikasi
    application = Application.builder().token(TOKEN).build()
    
    # Menambahkan handler untuk perintah
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_airdrops))
    application.add_handler(CommandHandler("search", search_command))
    
    # Handler untuk tombol inline
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Handler untuk pesan yang diteruskan
    application.add_handler(
        MessageHandler(filters.FORWARDED, handle_forwarded_message)
    )
    
    # Handler untuk pesan catatan
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_notes_message)
    )
    
    # Mulai polling
    logger.info("Bot mulai berjalan...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Jalankan server Flask di thread terpisah untuk mencegah Replit sleep
    keep_alive()
    
    # Jalankan bot
    main() 