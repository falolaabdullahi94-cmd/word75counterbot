import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Configuration ---
# Get the bot token from the environment variable set on Railway
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set!")

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    welcome_message = (
        "👋 Hello! I'm Word75 Counter Bot.\n\n"
        "Send me text and I'll analyze it for you!\n\n"
        "📌 Commands:\n"
        "/count <your text> - Count words, characters, and sentences\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    help_message = (
        "📖 *How to use me:*\n\n"
        "Simply send:\n"
        "`/count Your text here`\n\n"
        "I will reply with:\n"
        "• 📝 Word count\n"
        "• 🔠 Character count\n"
        "• 📄 Sentence count"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def count_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count words, characters, and sentences in the provided text."""
    # Get the text after the /count command
    user_text = ' '.join(context.args)

    if not user_text:
        await update.message.reply_text(
            "⚠️ Please provide text to analyze.\n\n"
            "Example: `/count Hello world! This is a test.`",
            parse_mode='Markdown'
        )
        return

    # Perform analysis
    word_count = len(user_text.split())
    char_count = len(user_text)

    # Count sentences (ending with ., !, or ?)
    sentence_count = len(re.findall(r'[.!?]+', user_text))
    if sentence_count == 0 and len(user_text) > 0:
        sentence_count = 1  # At least one sentence if there's text

    response = (
        f"📊 *Text Analysis Results*\n\n"
        f"📝 **Words:** {word_count}\n"
        f"🔠 **Characters:** {char_count}\n"
        f"📄 **Sentences:** {sentence_count}\n\n"
        f"📌 *Text analyzed:*\n"
        f"`{user_text[:200]}{'...' if len(user_text) > 200 else ''}`"
    )

    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    """Start the bot with long polling."""
    print("🚀 Starting Word75 Counter Bot...")
    print("📡 Using long polling mode")

    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("count", count_words))

    # Start the bot with long polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
