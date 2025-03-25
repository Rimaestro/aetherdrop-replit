from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import re
import datetime
from app.database import (
    add_airdrop, get_all_airdrops, get_airdrop_by_id, 
    search_airdrops, update_airdrop_status, add_notes, delete_airdrop
)
from app.config import AUTHORIZED_USER_ID

# Status yang tersedia untuk airdrop
AIRDROP_STATUSES = ["registered", "completed", "claimed", "failed"]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /start."""
    user_id = update.effective_user.id
    
    if user_id != AUTHORIZED_USER_ID and AUTHORIZED_USER_ID != 0:
        await update.message.reply_text("Maaf, Anda tidak diizinkan menggunakan bot ini.")
        return
    
    await update.message.reply_text(
        "👋 Selamat datang di AetherDrop Bot!\n\n"
        "Bot ini membantu Anda mencatat airdrop yang Anda ikuti.\n\n"
        "Cara menggunakan:\n"
        "- Teruskan pesan dari channel airdrop ke bot ini\n"
        "- Gunakan /list untuk melihat daftar airdrop Anda\n"
        "- Gunakan /search <kata kunci> untuk mencari airdrop\n"
        "- Gunakan /help untuk bantuan lebih lanjut"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /help."""
    user_id = update.effective_user.id
    
    if user_id != AUTHORIZED_USER_ID and AUTHORIZED_USER_ID != 0:
        await update.message.reply_text("Maaf, Anda tidak diizinkan menggunakan bot ini.")
        return
    
    help_text = (
        "📚 *AetherDrop Bot - Panduan Penggunaan* 📚\n\n"
        "*Perintah Dasar:*\n"
        "/start - Memulai bot\n"
        "/help - Menampilkan bantuan ini\n"
        "/list - Menampilkan semua airdrop yang tersimpan\n"
        "/search <kata kunci> - Mencari airdrop berdasarkan kata kunci\n\n"
        
        "*Pencatatan Airdrop:*\n"
        "• Teruskan pesan dari channel airdrop ke bot\n"
        "• Bot akan otomatis menyimpan informasi airdrop\n\n"
        
        "*Mengelola Airdrop:*\n"
        "• Gunakan tombol di bawah setiap airdrop untuk:\n"
        "  - Mengubah status\n"
        "  - Menambahkan catatan\n"
        "  - Menghapus airdrop\n\n"
        
        "*Status Airdrop:*\n"
        "• registered - Baru mendaftar\n"
        "• completed - Telah menyelesaikan persyaratan\n"
        "• claimed - Airdrop berhasil diklaim\n"
        "• failed - Gagal mendapatkan airdrop"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def extract_project_name(text):
    """Ekstrak nama proyek dari teks pesan."""
    # Mencoba mencari pola yang umum untuk nama proyek
    patterns = [
        r"(?i)project[:\s]+([^\n]+)",
        r"(?i)token[:\s]+([^\n]+)",
        r"(?i)airdrop[:\s]+([^\n]+)",
        r"(?i)name[:\s]+([^\n]+)",
        r"(?i)([a-zA-Z0-9]+(?:\s[a-zA-Z0-9]+){0,2})\s(?:airdrop|token)",
        r"(?i)([a-zA-Z0-9]+(?:\s[a-zA-Z0-9]+){0,2})\s(?:protocol|network)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    # Jika tidak ada pola yang cocok, ambil baris pertama
    first_line = text.split('\n')[0].strip()
    if first_line:
        # Batasi panjang nama proyek
        return first_line[:50]
    
    return "Unnamed Airdrop"

async def extract_registration_link(text):
    """Ekstrak link pendaftaran dari teks pesan."""
    # Mencari URL dalam teks
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, text)
    
    # Filter link yang mungkin merupakan link pendaftaran
    registration_keywords = ['register', 'signup', 'sign-up', 'join', 'claim', 'airdrop', 'app', 'dapp']
    
    for url in urls:
        for keyword in registration_keywords:
            if keyword in url.lower():
                return url
    
    # Jika tidak ada yang cocok dengan kata kunci, kembali URL pertama saja
    return urls[0] if urls else ""

async def generate_source_link(message):
    """Menghasilkan tautan ke pesan asli di channel."""
    if not message.forward_from_chat:
        return ""
    
    chat_id = message.forward_from_chat.id
    message_id = message.forward_from_message_id
    
    # Format untuk tautan pesan Telegram
    if chat_id < 0:
        # Channel atau grup publik, format: https://t.me/c/{chat_id}/{message_id}
        # Untuk channel publik dengan username, format bisa: https://t.me/{username}/{message_id}
        if message.forward_from_chat.username:
            return f"https://t.me/{message.forward_from_chat.username}/{message_id}"
        else:
            # Untuk channel pribadi, menggunakan format c/chat_id tanpa -100 di depan
            formatted_chat_id = str(chat_id)[4:] if str(chat_id).startswith('-100') else str(chat_id)[1:]
            return f"https://t.me/c/{formatted_chat_id}/{message_id}"
    
    return ""

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani pesan yang diteruskan dari channel airdrop."""
    user_id = update.effective_user.id
    
    if user_id != AUTHORIZED_USER_ID and AUTHORIZED_USER_ID != 0:
        await update.message.reply_text("Maaf, Anda tidak diizinkan menggunakan bot ini.")
        return
    
    message = update.message
    
    # Memeriksa apakah pesan diteruskan
    if not message.forward_date:
        await message.reply_text("Silakan teruskan pesan dari channel airdrop.")
        return
    
    # Mendapatkan informasi dari pesan
    forward_date = message.forward_date
    source_channel = message.forward_from_chat.title if message.forward_from_chat else "Unknown"
    message_text = message.text or message.caption or ""
    original_message_id = message.forward_from_message_id
    
    # Mendapatkan tautan sumber pesan
    source_link = await generate_source_link(message)
    
    # Ekstrak informasi penting
    project_name = await extract_project_name(message_text)
    registration_link = await extract_registration_link(message_text)
    
    # Simpan ke database
    airdrop_id = add_airdrop(
        project_name=project_name,
        description=message_text[:100] + "..." if len(message_text) > 100 else message_text,
        registration_link=registration_link,
        forward_date=forward_date,
        source_channel=source_channel,
        original_message_id=original_message_id,
        message_text=message_text,
        source_link=source_link  # Tambahkan link sumber
    )
    
    # Buat keyboard inline untuk tindakan selanjutnya
    keyboard = [
        [
            InlineKeyboardButton("Lihat Detail", callback_data=f"view_{airdrop_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    source_link_text = f"\nLink Sumber: {source_link}" if source_link else ""
    
    await message.reply_text(
        f"✅ Airdrop {project_name} berhasil disimpan!\n\n"
        f"ID: {airdrop_id}\n"
        f"Sumber: {source_channel}\n"
        f"Tanggal: {forward_date.strftime('%d-%m-%Y %H:%M')}\n"
        f"{source_link_text}\n"
        f"Link Registrasi: {registration_link}",
        reply_markup=reply_markup
    )

async def list_airdrops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /list."""
    user_id = update.effective_user.id
    
    if user_id != AUTHORIZED_USER_ID and AUTHORIZED_USER_ID != 0:
        await update.message.reply_text("Maaf, Anda tidak diizinkan menggunakan bot ini.")
        return
    
    airdrops = get_all_airdrops()
    
    if not airdrops:
        await update.message.reply_text("Anda belum menyimpan airdrop apa pun.")
        return
    
    for airdrop in airdrops[:10]:  # Batasi ke 10 hasil terbaru
        keyboard = [
            [InlineKeyboardButton("Lihat Detail", callback_data=f"view_{airdrop['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status_emoji = {
            "registered": "📝",
            "completed": "✅",
            "claimed": "💰",
            "failed": "❌"
        }.get(airdrop["status"], "📝")
        
        await update.message.reply_text(
            f"{status_emoji} *{airdrop['project_name']}*\n"
            f"Status: {airdrop['status']}\n"
            f"Tanggal: {datetime.datetime.fromisoformat(airdrop['forward_date']).strftime('%d-%m-%Y')}\n"
            f"Sumber: {airdrop['source_channel']}\n\n"
            f"{airdrop['description']}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    if len(airdrops) > 10:
        await update.message.reply_text(
            f"Menampilkan 10 dari {len(airdrops)} airdrop.\n"
            f"Gunakan /search <kata kunci> untuk mencari airdrop tertentu."
        )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /search."""
    user_id = update.effective_user.id
    
    if user_id != AUTHORIZED_USER_ID and AUTHORIZED_USER_ID != 0:
        await update.message.reply_text("Maaf, Anda tidak diizinkan menggunakan bot ini.")
        return
    
    # Memeriksa apakah ada kata kunci
    if not context.args:
        await update.message.reply_text("Gunakan: /search <kata kunci>")
        return
    
    keyword = " ".join(context.args)
    results = search_airdrops(keyword)
    
    if not results:
        await update.message.reply_text(f"Tidak ditemukan airdrop dengan kata kunci '{keyword}'.")
        return
    
    await update.message.reply_text(f"Ditemukan {len(results)} airdrop dengan kata kunci '{keyword}':")
    
    for airdrop in results[:10]:  # Batasi ke 10 hasil
        keyboard = [
            [InlineKeyboardButton("Lihat Detail", callback_data=f"view_{airdrop['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status_emoji = {
            "registered": "📝",
            "completed": "✅",
            "claimed": "💰",
            "failed": "❌"
        }.get(airdrop["status"], "📝")
        
        await update.message.reply_text(
            f"{status_emoji} *{airdrop['project_name']}*\n"
            f"Status: {airdrop['status']}\n"
            f"Tanggal: {datetime.datetime.fromisoformat(airdrop['forward_date']).strftime('%d-%m-%Y')}\n"
            f"Sumber: {airdrop['source_channel']}\n\n"
            f"{airdrop['description']}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani callback dari tombol inline."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != AUTHORIZED_USER_ID and AUTHORIZED_USER_ID != 0:
        await query.edit_message_text("Maaf, Anda tidak diizinkan menggunakan bot ini.")
        return
    
    data = query.data
    
    if data.startswith("view_"):
        # Menampilkan detail airdrop
        airdrop_id = int(data.split("_")[1])
        airdrop = get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.edit_message_text("Airdrop tidak ditemukan.")
            return
        
        # Keyboard untuk tindakan
        keyboard = [
            [
                InlineKeyboardButton("Status ⚙️", callback_data=f"status_{airdrop_id}"),
                InlineKeyboardButton("Catatan 📝", callback_data=f"notes_{airdrop_id}")
            ],
            [
                InlineKeyboardButton("Hapus 🗑️", callback_data=f"delete_{airdrop_id}"),
                InlineKeyboardButton("Kembali 🔙", callback_data="back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status_emoji = {
            "registered": "📝",
            "completed": "✅",
            "claimed": "💰",
            "failed": "❌"
        }.get(airdrop["status"], "📝")
        
        notes_text = f"\n\n📝 *Catatan:*\n{airdrop['notes']}" if airdrop['notes'] else ""
        source_link_text = f"\n*Link Sumber:* {airdrop['source_link']}" if 'source_link' in airdrop and airdrop['source_link'] else ""
        
        message_text = (
            f"{status_emoji} *{airdrop['project_name']}*\n\n"
            f"*Status:* {airdrop['status']}\n"
            f"*Tanggal:* {datetime.datetime.fromisoformat(airdrop['forward_date']).strftime('%d-%m-%Y %H:%M')}\n"
            f"*Sumber:* {airdrop['source_channel']}{source_link_text}\n\n"
            f"*Link Registrasi:* {airdrop['registration_link']}"
            f"{notes_text}\n\n"
            f"*Pesan Asli:*\n```\n{airdrop['message_text'][:300]}```\n"
            f"{'...' if len(airdrop['message_text']) > 300 else ''}"
        )
        
        await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    elif data.startswith("status_"):
        # Mengubah status airdrop
        airdrop_id = int(data.split("_")[1])
        airdrop = get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.edit_message_text("Airdrop tidak ditemukan.")
            return
        
        # Keyboard untuk status
        keyboard = []
        for status in AIRDROP_STATUSES:
            emoji = "✓" if status == airdrop["status"] else ""
            keyboard.append([InlineKeyboardButton(f"{status.capitalize()} {emoji}", callback_data=f"set_status_{airdrop_id}_{status}")])
        
        keyboard.append([InlineKeyboardButton("Kembali 🔙", callback_data=f"view_{airdrop_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Pilih status untuk airdrop *{airdrop['project_name']}*:\n\n"
            f"Status saat ini: *{airdrop['status']}*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif data.startswith("set_status_"):
        # Mengatur status baru untuk airdrop
        _, _, airdrop_id, status = data.split("_")
        airdrop_id = int(airdrop_id)
        
        success = update_airdrop_status(airdrop_id, status)
        
        if success:
            await query.edit_message_text(
                f"Status berhasil diubah menjadi: *{status}*\n\n"
                f"Kembali ke detail airdrop dalam 3 detik...",
                parse_mode="Markdown"
            )
            
            # Setelah beberapa detik, kembali ke detail airdrop
            context.job_queue.run_once(
                lambda _: query.edit_message_text(
                    text="Memuat detail airdrop...",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Detail", callback_data=f"view_{airdrop_id}")
                    ]])
                ),
                3
            )
        else:
            await query.edit_message_text(
                "Gagal mengubah status. Silakan coba lagi.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Kembali", callback_data=f"view_{airdrop_id}")
                ]])
            )
    
    elif data.startswith("notes_"):
        # Menampilkan prompt untuk menambahkan/mengubah catatan
        airdrop_id = int(data.split("_")[1])
        airdrop = get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.edit_message_text("Airdrop tidak ditemukan.")
            return
        
        # Simpan ID airdrop di data pengguna
        context.user_data["editing_notes_for"] = airdrop_id
        
        await query.edit_message_text(
            f"Masukkan catatan untuk airdrop *{airdrop['project_name']}*:\n\n"
            f"Catatan saat ini: {airdrop['notes'] or 'Tidak ada'}\n\n"
            f"Balas pesan ini dengan catatan baru.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Batal", callback_data=f"view_{airdrop_id}")
            ]])
        )
    
    elif data.startswith("delete_"):
        # Konfirmasi penghapusan airdrop
        airdrop_id = int(data.split("_")[1])
        airdrop = get_airdrop_by_id(airdrop_id)
        
        if not airdrop:
            await query.edit_message_text("Airdrop tidak ditemukan.")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("Ya, Hapus", callback_data=f"confirm_delete_{airdrop_id}"),
                InlineKeyboardButton("Batal", callback_data=f"view_{airdrop_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Anda yakin ingin menghapus airdrop *{airdrop['project_name']}*?\n\n"
            f"Tindakan ini tidak dapat dibatalkan.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif data.startswith("confirm_delete_"):
        # Menghapus airdrop
        airdrop_id = int(data.split("_")[2])
        
        success = delete_airdrop(airdrop_id)
        
        if success:
            await query.edit_message_text("Airdrop berhasil dihapus.")
        else:
            await query.edit_message_text(
                "Gagal menghapus airdrop. Silakan coba lagi.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Kembali", callback_data=f"view_{airdrop_id}")
                ]])
            )
    
    elif data == "back":
        # Kembali ke daftar airdrop
        await query.edit_message_text(
            "Gunakan /list untuk melihat daftar airdrop Anda."
        )

async def handle_notes_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani pesan catatan untuk airdrop."""
    user_id = update.effective_user.id
    
    if user_id != AUTHORIZED_USER_ID and AUTHORIZED_USER_ID != 0:
        await update.message.reply_text("Maaf, Anda tidak diizinkan menggunakan bot ini.")
        return
    
    # Memeriksa apakah pengguna sedang mengedit catatan
    if "editing_notes_for" not in context.user_data:
        return
    
    airdrop_id = context.user_data["editing_notes_for"]
    new_notes = update.message.text
    
    success = add_notes(airdrop_id, new_notes)
    
    if success:
        await update.message.reply_text(
            "Catatan berhasil disimpan.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Lihat Detail", callback_data=f"view_{airdrop_id}")
            ]])
        )
    else:
        await update.message.reply_text(
            "Gagal menyimpan catatan. Silakan coba lagi.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Kembali", callback_data=f"view_{airdrop_id}")
            ]])
        )
    
    # Hapus status pengeditan catatan
    del context.user_data["editing_notes_for"] 