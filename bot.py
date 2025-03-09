import logging
import pandas as pd
from fuzzywuzzy import process
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ✅ Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ✅ Replace with your Telegram Bot Token
TOKEN = "5572298787:AAEvie8_2VXsiG4DoBA43rNx9D3pEVG69W4"

# ✅ Load book data from Excel
BOOKS_FILE = "books.xlsx"

try:
    df = pd.read_excel(BOOKS_FILE, engine="openpyxl")
except Exception as e:
    logging.error(f"Error loading books file: {e}")
    df = None

# ✅ Function to handle /start command
async def start(update: Update, context):
    await update.message.reply_text("📚 Welcome to *Prep Library*! Send a book name to get all related books.")

# ✅ Book search function
def search_books(query, limit=3):
    if df is None:
        return []

    book_names = df["BOOK_NAME"].tolist()
    matches = process.extract(query, book_names, limit=limit)

    results = []
    for match in matches:
        if match[1] > 50:  # 50% match threshold
            book = df[df["BOOK_NAME"] == match[0]].iloc[0]
            results.append(book)
    
    return results

# ✅ Function to handle book search queries
async def handle_message(update: Update, context):
    query = update.message.text
    results = search_books(query)

    if not results:
        await update.message.reply_text("❌ No books found. Try another search!")
        return

    for book in results:
        caption = (
            f"📖 *{book['BOOK_NAME']}* \n"
            f"✍️ *Author:* {book['AUTHER']}\n"
            f"📅 *Edition:* {book['EDITION']}\n"
            f"───────────────\n"
            f"Click the buttons below to download or join our group!"
        )


        # ✅ Create multiple buttons
        keyboard = [
            [  # 1st row: Two buttons
                InlineKeyboardButton("📥 Download Link", url=book["DOWNLOAD_URL"]),
                InlineKeyboardButton("❓ How to Download", url="https://t.me/StudyRatna_2/42")
            ],
            [  # 2nd row: One button
                InlineKeyboardButton("📚 Join PrepLibrary", url="https://t.me/PrepLibrary_Discussion")
            ]
        ]

        # ✅ Attach buttons to message
        reply_markup = InlineKeyboardMarkup(keyboard)


        if pd.notna(book["COVER_IMAGE_FROM_URL"]):  # If image URL is available
            await update.message.reply_photo(
                photo=book["COVER_IMAGE_FROM_URL"], 
                caption=caption, 
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=reply_markup)

# ✅ Create the application and add handlers
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ✅ Run the bot
if __name__ == "__main__":
    logging.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
