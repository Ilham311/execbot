from pyrogram import Client, filters, idle
import io
import sys
from threading import Thread
import subprocess
from flask import Flask, redirect
import os

# Inisialisasi Userbot dengan sesi string
SESSION_STRING = "BQAf70YAfSwTp6zgdD4v5QIMHfi6jTYBvgay5-wH3H9Kkm427AfdlHZqFRDRDO4Z4oCdx7KhxbNsOxJv-S8l6ywVPNcjEhYojjGCSL8te3Cmq0jltNtDoGlT_DeHC8j5Prahs6ASnu2G7i4_zpAKqdN6gnOPYPxVXb0HB6YdTtHXhRaJ9MjROCIj96fjCvp10NOOf1OXwNxxYMBQVTlg4H6KzmlNJO0fh4VcQPU8reE7ti045B95CFK4c-J61RMijFgwo_WO5i9ShsXc_EZEHL-R7uuCGlRkYLTHhwz5_MwwfW7wvPCM16EIiUmWVCQvIXCQJwRmeI0B8UDUpLc4CiN-RC8uEwAAAAA87_QTAA"
app = Client("userbot_exec", session_string=SESSION_STRING)

# Flask application
web_app = Flask(__name__)

# Route untuk pengalihan sederhana
@web_app.route('/')
def home():
    return "Selamat datang di fake website! Ini halaman utama."

@web_app.route('/redirect')
def redirect_to():
    # Pengalihan ke URL lain (contoh: ke Google)
    return redirect("https://www.google.com", code=302)

def sanitize_code(code):
    """
    Menghapus karakter non-printable seperti spasi non-breaking (U+00A0).
    """
    return code.replace('\xa0', ' ')

def install_package(package_name):
    """
    Menginstal paket Python menggunakan pip.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return f"**Paket '{package_name}' berhasil diinstal.**"
    except Exception as e:
        return f"**Gagal menginstal '{package_name}':** {e}"

@app.on_message(filters.command("exec", prefixes=".") & filters.me)
async def exec_code(client, message):
    """
    Jalankan kode Python yang diterima melalui perintah .exec.
    """
    if len(message.text.split()) < 2:
        await message.reply("**Harap berikan kode Python untuk dijalankan.**")
        return

    code = message.text[len(".exec "):]  # Ambil kode setelah perintah .exec
    code = sanitize_code(code)  # Sanitasi kode untuk menghapus karakter non-printable
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    try:
        exec(code, {"client": client})  # Eksekusi kode Python
    except ImportError as e:
        # Parsing nama modul yang hilang
        missing_module = str(e).split("named ")[-1].replace("'", "")
        result = f"**Error:** {e}\n\n**Menginstal modul `{missing_module}`...**"
        await message.reply(result)
        install_message = install_package(missing_module)
        await message.reply(install_message)
    except Exception as e:
        result = f"**Error saat menjalankan kode:**\n`{e}`"
    else:
        result = redirected_output.getvalue().strip() or "**Kode berhasil dijalankan tanpa output.**"
    finally:
        sys.stdout = old_stdout

    # Kirim hasil eksekusi ke Telegram
    if len(result) > 4096:  # Jika hasil terlalu panjang
        with io.BytesIO(result.encode()) as file:
            file.name = "result.txt"
            await message.reply_document(file, caption="**Hasil Eksekusi**")
    else:
        # Mengirim hasil eksekusi dalam potongan jika panjangnya besar
        if len(result) > 2048:
            await message.reply(f"**Output Terlalu Panjang, Membagi Potongan Output**\n```\n{result[:2048]}\n```")
            await message.reply(f"```\n{result[2048:]}\n```")
        else:
            await message.reply(f"**Output:**\n```\n{result}\n```")

def run_flask():
    port = int(os.getenv("PORT", 5000))  # Default ke 5000
    web_app.run(host="0.0.0.0", port=port, threaded=True)

if __name__ == "__main__":
    print("Bot dan Web Server sedang berjalan...")
    try:
        # Jalankan Flask dan Pyrogram
        thread = Thread(target=run_flask)
        thread.start()
        app.start()
        idle()  # Pastikan Pyrogram tetap berjalan
    except KeyboardInterrupt:
        print("Menutup aplikasi...")
    finally:
        app.stop()
