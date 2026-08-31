"""
Toshkent metro yo'llari haqida ma'lumot beruvchi Telegram bot.

/start bosilganda 4ta metro yo'li tugmasi chiqadi. Foydalanuvchi birini
tanlasa, o'sha yo'lning bekatlar ro'yxati ko'rsatiladi.

STANSIYALAR RO'YXATINI O'ZINGIZ TO'LDIRING — pastdagi LINES lug'atiga qarang.
"""
import os
import logging

from dotenv import load_dotenv
load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# ============================================================
# STANSIYALAR RO'YXATI — o'zingiz to'ldiring.
# Har bir yo'lning bekatlarini ro'yxat ko'rinishida, kelish
# tartibida (masalan janubdan shimolga) yozing.
# ============================================================
LINES = {
    "ozbekiston": {
        "title": "O'zbekiston yo'li",
        "stations": [
            # "Beruniy",
            # "Chorsu",
            # ... shu yerga to'ldiring
        ],
    },
    "chilonzor": {
        "title": "Chilonzor yo'li",
        "stations": [
            # "Olmazor",
            # "Chilonzor",
            # ... shu yerga to'ldiring
        ],
    },
    "halqa": {
        "title": "Xalqa yo'li",
        "stations": [
            # ... shu yerga to'ldiring
        ],
    },
    "yunusobod": {
        "title": "Yunusobod yo'li",
        "stations": [
            # ... shu yerga to'ldiring
        ],
    },
}


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """4ta metro yo'li tugmasini chiqaradi."""
    buttons = [
        [InlineKeyboardButton(LINES["ozbekiston"]["title"], callback_data="line:ozbekiston")],
        [InlineKeyboardButton(LINES["chilonzor"]["title"], callback_data="line:chilonzor")],
        [InlineKeyboardButton(LINES["halqa"]["title"], callback_data="line:halqa")],
        [InlineKeyboardButton(LINES["yunusobod"]["title"], callback_data="line:yunusobod")],
    ]
    return InlineKeyboardMarkup(buttons)


def back_keyboard() -> InlineKeyboardMarkup:
    """Bosh menyuga qaytish tugmasi."""
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚇 Toshkent metro yo'nalishlaridan birini tanlang:",
        reply_markup=main_menu_keyboard(),
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Telegram'ga "bosildi" signalini yuborish

    if query.data == "back":
        await query.edit_message_text(
            "🚇 Toshkent metro yo'nalishlaridan birini tanlang:",
            reply_markup=main_menu_keyboard(),
        )
        return

    # "line:xxx" formatidan kalitni ajratib olamiz
    line_key = query.data.split(":", 1)[1]
    line = LINES.get(line_key)

    if not line or not line["stations"]:
        await query.edit_message_text(
            f"🚇 {line['title'] if line else ''}\n\n"
            "Bu yo'l uchun bekatlar ro'yxati hali kiritilmagan.",
            reply_markup=back_keyboard(),
        )
        return

    stations_text = "\n".join(f"{i+1}. {name}" for i, name in enumerate(line["stations"]))
    await query.edit_message_text(
        f"🚇 <b>{line['title']}</b>\n\n{stations_text}",
        parse_mode="HTML",
        reply_markup=back_keyboard(),
    )


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))

    logger.info("Metro bot ishga tushdi...")
    application.run_polling()


if __name__ == "__main__":
    main()
