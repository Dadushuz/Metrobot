"""
Toshkent metro yo'llari haqida ma'lumot beruvchi Telegram bot.

/start bosilganda 4ta metro yo'li tugmasi chiqadi. Foydalanuvchi birini
tanlasa, Telegram ICHIDA veb-sahifa ochiladi (Web App) — u yerda bekatlar
ro'yxati va ular orasida "harakatlanadigan" poyezd animatsiyasi ko'rsatiladi.

DIQQAT: bu animatsiya HAQIQIY GPS ma'lumoti EMAS (Toshkent metrosining
ochiq real-vaqt API'si yo'q) — bu faqat ishonarli ko'rinishdagi simulyatsiya.

STANSIYALAR RO'YXATINI O'ZINGIZ TO'LDIRING — pastdagi LINES lug'atiga qarang.
"""
import os
import logging
import threading

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

from webapp_render import render_line_page

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
# Railway'da "Generate Domain" orqali olingan havola, masalan:
# https://metrobot-production.up.railway.app  (oxirida / bo'lmasin)
WEBAPP_BASE_URL = os.environ["WEBAPP_BASE_URL"].rstrip("/")

# ============================================================
# STANSIYALAR RO'YXATI — o'zingiz to'ldiring (janubdan-shimolga
# yoki boshlanish nuqtasidan oxirigacha tartibda yozing).
# ============================================================
LINES = {
    "ozbekiston": {
        "title": "O'zbekiston yo'li",
        "color": "#2196F3",
        "stations": [
            "Beruniy",
            "Tinchlik",
            "Chorsu",
            "Alisher Navoiy",
            "G'afur G'ulom",
            "O'zbekiston",
            "Oybek",
            "Toshkent",
            "Kosmonavtlar",
            "Mashinasozlar",
            "Do'stlik",
        ],
    },
    "chilonzor": {
        "title": "Chilonzor yo'li",
        "color": "#E53935",
        "stations": [
            # "Olmazor",
            # "Chilonzor",
        ],
    },
    "halqa": {
        "title": "Xalqa yo'li",
        "color": "#FDD835",
        "stations": [
        ],
    },
    "yunusobod": {
        "title": "Yunusobod yo'li",
        "color": "#43A047",
        "stations": [
        ],
    },
}

# ============================================================
# VEB-SERVER (Flask) — Telegram Web App shu orqali ochiladi
# ============================================================
flask_app = Flask(__name__)


@flask_app.route("/line/<line_key>")
def line_page(line_key):
    line = LINES.get(line_key)
    if not line:
        return Response("Yo'l topilmadi", status=404)
    html = render_line_page(line["title"], line["color"], line["stations"])
    return Response(html, mimetype="text/html")


def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)


# ============================================================
# TELEGRAM BOT
# ============================================================
def main_menu_keyboard() -> InlineKeyboardMarkup:
    def btn(key):
        url = f"{WEBAPP_BASE_URL}/line/{key}"
        return InlineKeyboardButton(LINES[key]["title"], web_app=WebAppInfo(url=url))

    return InlineKeyboardMarkup(
        [[btn("ozbekiston")], [btn("chilonzor")], [btn("halqa")], [btn("yunusobod")]]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚇 Toshkent metro yo'nalishlaridan birini tanlang:",
        reply_markup=main_menu_keyboard(),
    )


def main():
    # Flask serverni alohida oqimda (thread) ishga tushiramiz,
    # shunda u Telegram bot bilan bir vaqtda ishlaydi.
    threading.Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    logger.info("Metro bot va veb-server ishga tushdi...")
    application.run_polling()


if __name__ == "__main__":
    main()
