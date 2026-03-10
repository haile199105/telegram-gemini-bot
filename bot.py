import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

# Load tokens from Railway environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if tokens are set
if not TELEGRAM_TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set!")
    exit(1)
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not set!")
    exit(1)

# Initialize Gemini AI with current model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')  # Updated to current model

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    await update.message.reply_text(
        "👋 Hi! I'm your AI assistant powered by Gemini.\n\n"
        "Send me any message and I'll respond!\n"
        "Use /help to see available commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    await update.message.reply_text(
        "📋 **Available Commands:**\n\n"
        "/start - Welcome message\n"
        "/help - Show this help\n\n"
        "**Just send any message** and I'll reply using AI!\n"
        "Ask me anything about programming, IT, or general topics."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages with Gemini AI."""
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Create a prompt for Gemini
        prompt = f"""
        You are Haile, a friendly IT teacher and developer based in Ethiopia.
        
        User's name: {user_name}
        User's message: {user_message}
        
        Respond in a helpful, friendly way. Keep answers clear and educational.
        If asked about technical topics, explain them simply.
        """
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Send the response (Telegram has 4096 character limit)
        reply_text = response.text[:4000]
        await update.message.reply_text(reply_text)

    except Exception as e:
        print(f"AI Error: {e}")
        await update.message.reply_text(
            "❌ Sorry, I encountered an error. Please try again in a moment."
        )

if __name__ == "__main__":
    print("Starting bot...")
    print(f"Telegram Token: {TELEGRAM_TOKEN[:5]}...")
    print(f"Gemini API Key: {GEMINI_API_KEY[:5]}...")
    
    # Create the Application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    # Start the bot (this blocks until stopped)
    app.run_polling()
