# AetherDrop Bot untuk Replit

Bot Telegram untuk mencatat dan mengelola airdrop cryptocurrency secara otomatis. Versi ini telah dioptimalkan untuk berjalan di [Replit](https://replit.com) tanpa perlu VPS atau kartu kredit.

## Fitur

- Menyimpan pesan yang diteruskan dari channel airdrop
- Otomatis mengekstrak nama proyek dan link pendaftaran
- Melacak status airdrop (registered, completed, claimed, failed)
- Menambahkan catatan untuk setiap airdrop
- Mencari airdrop berdasarkan kata kunci
- Menampilkan daftar semua airdrop yang tersimpan
- Menghapus airdrop yang tidak diperlukan lagi
- **Anti-sleep system** untuk menjaga bot tetap online 24/7 di Replit

## Pengaturan di Replit

### 1. Buat Repl Baru

1. Daftar/login ke [Replit](https://replit.com)
2. Klik tombol "+ Create" dan pilih "Import from GitHub"
3. Paste URL repository GitHub Anda (jika sudah di-upload) atau upload semua file secara manual
4. Pilih "Python" sebagai bahasa

### 2. Mengatur Secrets (Variabel Lingkungan)

Di Replit, Anda perlu mengatur variabel lingkungan menggunakan fitur Secrets:

1. Di sidebar kiri, klik pada ikon kunci (🔑) atau "Secrets"
2. Tambahkan dua secrets:
   - Key: `TELEGRAM_BOT_TOKEN` | Value: Token dari BotFather
   - Key: `AUTHORIZED_USER_ID` | Value: ID Telegram Anda (angka)

Untuk mendapatkan token dan ID:
- **Bot Token**: Hubungi [@BotFather](https://t.me/BotFather) di Telegram, ikuti instruksi untuk membuat bot baru
- **User ID**: Hubungi [@userinfobot](https://t.me/userinfobot) di Telegram untuk mendapatkan ID Anda

### 3. Jalankan Bot

1. Klik tombol "Run" di bagian atas
2. Anda akan melihat output di console dan web server akan berjalan
3. Replit akan memberikan URL untuk web server (biasanya di format `https://aetherdrop-bot.yourusername.repl.co`)
4. Catat URL ini untuk langkah berikutnya

### 4. Setup UptimeRobot untuk Menjaga Bot Aktif 24/7

Replit akan "tertidur" jika tidak ada aktivitas. Untuk menjaga bot tetap aktif:

1. Daftar akun gratis di [UptimeRobot](https://uptimerobot.com)
2. Setelah login, klik "Add New Monitor"
3. Pilih "HTTP(s)" sebagai jenis monitor
4. Masukkan nama untuk monitor (misalnya "AetherDrop Bot")
5. Paste URL Replit Anda yang didapat di langkah 3
6. Atur interval monitoring ke 5 menit
7. Klik "Create Monitor"

UptimeRobot akan melakukan ping ke URL Anda setiap 5 menit, mencegah Replit tertidur.

## Cara Penggunaan Bot

1. Mulai percakapan dengan bot Anda di Telegram
2. Gunakan perintah `/start` untuk memulai
3. Teruskan pesan dari channel airdrop ke bot untuk menyimpan airdrop baru
4. Gunakan perintah `/list` untuk melihat semua airdrop yang tersimpan
5. Gunakan perintah `/search <kata kunci>` untuk mencari airdrop tertentu
6. Gunakan tombol di bawah setiap airdrop untuk mengelola airdrop

## Troubleshooting

### Bot Tidak Merespon

1. Periksa log di Replit untuk error
2. Pastikan TELEGRAM_BOT_TOKEN benar
3. Periksa apakah UptimeRobot berjalan dengan benar
4. Coba klik "Stop" dan kemudian "Run" lagi di Replit

### Pesan "Forbidden" atau Masalah dengan Webhook

1. Pastikan token bot benar
2. Pastikan bot belum di-set dengan webhook di tempat lain
3. Reset webhook dengan mengunjungi: `https://api.telegram.org/bot<token>/deleteWebhook`

### Bot Error Setelah Beberapa Waktu

Replit memiliki batasan sumber daya. Jika bot mengalami error setelah berjalan lama:
1. Periksa jika database terlalu besar
2. Coba restart bot dengan menekan "Stop" dan "Run"
3. Pastikan Anda berada dalam batas free tier Replit

## Perbedaan dengan Versi VPS

Versi Replit ini sedikit berbeda dari versi VPS:

1. Menggunakan sistem anti-sleep dengan Flask server
2. Struktur folder lebih terorganisir dengan package Python
3. Menyimpan credentials di Secrets Replit bukan di file .env

## Lisensi

MIT License 