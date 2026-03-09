import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from google.genai import Client, types

# Load tokens from Railway environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini AI client
client = Client(api_key=GEMINI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        # Ask Gemini to respond like you
        response = client.generate_text(
            model="gemini-1.5",
            prompt=f"You are Haile, a friendly IT teacher. Explain clearly: {user_message}"
        )
        await update.message.reply_text(response.text)

    except Exception as e:
        print("AI Error:", e)
        await update.message.reply_text("AI error, please try again.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # Handle all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Start the bot
    app.run_polling()
