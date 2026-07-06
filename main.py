import os
import re
import logging
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ----------------------------
# CONFIGURATION & LOGGING
# ----------------------------

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    logger.error("❌ TELEGRAM_TOKEN environment variable not set!")
    logger.error("📝 Please set it in Railway: Variables -> Add Variable")
    sys.exit(1)

logger.info("✅ Bot token loaded successfully")

# ----------------------------
# COMMAND HANDLERS
# ----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📝 Count Text", callback_data="count"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        "👋 *Hello! I'm Word75 Counter Bot*\n\n"
        "I can analyze any text you send me!\n\n"
        "📌 *Quick Commands:*\n"
        "• `/count <text>` - Count words, characters, sentences\n"
        "• `/stats` - Show bot statistics\n"
        "• `/help` - View all commands\n\n"
        "💡 *Or just send me any text and I'll count it!*"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    logger.info(f"User {update.effective_user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send detailed help message."""
    help_message = (
        "📖 *How to use Word75 Counter Bot*\n\n"
        "📝 *Commands:*\n"
        "`/count` <your text> - Count words, characters, sentences\n"
        "`/stats` - Show bot usage statistics\n"
        "`/start` - Show welcome message\n"
        "`/help` - Show this help\n\n"
        "🔍 *Examples:*\n"
        "`/count Hello world!`\n"
        "`/count This is a test sentence.`\n\n"
        "📌 *Features:*\n"
        "• Word count\n"
        "• Character count (with/without spaces)\n"
        "• Sentence count\n"
        "• Unique word count\n"
        "• Reading time estimate\n\n"
        "⚡ *Tip:* You can just paste any text and I'll count it!"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def count_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count words, characters, and sentences in text."""
    # Get text after /count command
    user_text = ' '.join(context.args)
    
    # If no text provided, try to get from reply
    if not user_text and update.message.reply_to_message:
        user_text = update.message.reply_to_message.text or update.message.reply_to_message.caption
    
    if not user_text:
        await update.message.reply_text(
            "⚠️ *Please provide text to analyze!*\n\n"
            "Example:\n"
            "`/count Hello world! This is a test.`\n\n"
            "Or reply to a message with `/count`",
            parse_mode='Markdown'
        )
        return
    
    # Perform analysis
    await analyze_and_send(update, context, user_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages (auto-count)."""
    user_text = update.message.text
    
    if not user_text:
        return
    
    # Only auto-analyze if text is reasonable length
    if len(user_text.split()) > 2:  # Don't auto-analyze short messages
        await analyze_and_send(update, context, user_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics."""
    stats_message = (
        "📊 *Bot Statistics*\n\n"
        "👤 *User ID:* " + str(update.effective_user.id) + "\n"
        "🤖 *Bot Status:* Online ✅\n"
        "⚡ *Version:* 2.0\n"
        "📅 *Date:* " + update.message.date.strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
        "💡 *Features:*\n"
        "• Word counting\n"
        "• Character counting\n"
        "• Sentence analysis\n"
        "• Reading time estimation"
    )
    await update.message.reply_text(stats_message, parse_mode='Markdown')

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------

async def analyze_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Analyze text and send results."""
    try:
        # Basic counts
        word_count = len(text.split())
        char_count = len(text)
        char_no_space = len(text.replace(" ", ""))
        
        # Sentence count
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()]) 
        if sentence_count == 0 and len(text) > 0:
            sentence_count = 1
            
        # Unique words
        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = len(set(words))
        
        # Average word length
        avg_word_length = char_no_space / word_count if word_count > 0 else 0
        
        # Reading time (approx 200 words per minute)
        reading_time = max(1, round(word_count / 200))
        
        # Character distribution
        digits = sum(c.isdigit() for c in text)
        letters = sum(c.isalpha() for c in text)
        spaces = text.count(' ')
        punctuation = len(text) - digits - letters - spaces
        
        # Create response
        response = (
            f"📊 *Text Analysis Results*\n"
            f"{'─' * 20}\n\n"
            f"📝 *Words:* {word_count:,}\n"
            f"🔤 *Characters:* {char_count:,}\n"
            f"📐 *Characters (no spaces):* {char_no_space:,}\n"
            f"📄 *Sentences:* {sentence_count:,}\n"
            f"🌟 *Unique Words:* {unique_words:,}\n"
            f"📏 *Avg Word Length:* {avg_word_length:.1f} chars\n"
            f"⏱️ *Reading Time:* ~{reading_time} min{'s' if reading_time > 1 else ''}\n\n"
            f"📊 *Character Breakdown:*\n"
            f"• Letters: {letters:,}\n"
            f"• Digits: {digits:,}\n"
            f"• Spaces: {spaces:,}\n"
            f"• Punctuation: {punctuation:,}\n\n"
            f"📌 *Preview:*\n"
            f"`{text[:150]}{'...' if len(text) > 150 else ''}`"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info(f"Analyzed text for user {update.effective_user.id}: {word_count} words")
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        await update.message.reply_text(
            "❌ *Error analyzing text.* Please try again.",
            parse_mode='Markdown'
        )

# ----------------------------
# BUTTON CALLBACKS
# ----------------------------

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "count":
        await query.edit_message_text(
            "📝 *Send me text to count!*\n\n"
            "Use `/count <your text>` or just paste your text.",
            parse_mode='Markdown'
        )
    elif query.data == "help":
        await query.edit_message_text(
            "📖 *Help*\n\n"
            "Send `/count <text>` to analyze text.\n"
            "Or just paste any text and I'll auto-analyze it!\n\n"
            "Use `/stats` to see bot info.",
            parse_mode='Markdown'
        )

# ----------------------------
# ERROR HANDLER
# ----------------------------

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")

# ----------------------------
# MAIN FUNCTION
# ----------------------------

def main():
    """Start the bot."""
    logger.info("🚀 Starting Word75 Counter Bot...")
    
    try:
        # Create application
        application = Application.builder().token(TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("count", count_words))
        application.add_handler(CommandHandler("stats", stats_command))
        
        # Add message handler (auto-count)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add button callback handler
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        logger.info("📡 Bot is running with long polling...")
        logger.info("✅ Ready to accept messages!")
        
        # Start polling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
