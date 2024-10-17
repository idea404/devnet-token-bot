import logging
import sqlite3
from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ------------------------#
#        Logging          #
# ------------------------#
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s- %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ------------------------#
#        Env              #
# ------------------------#

load_dotenv()

# ------------------------#
#      Database Setup     #
# ------------------------#

# Database connection
conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

# Initialize database table
def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            handle TEXT,
            assigned_at TIMESTAMP DEFAULT NULL
        )
    ''')

    # == TESTS: add default data, timestamp May 1st 2024 ==

    # cursor.execute('''
    #     INSERT INTO urls (url, handle, assigned_at) VALUES
    #         ('https://rpc.ankr.com/eth_sepolia', 'xidea404', '2024-05-01 00:00:00')
    # ''')

    # add some rpc urls with no usernames, no timestamp
    # cursor.execute('''
    #     INSERT INTO urls (url, handle, assigned_at) VALUES
    #         ('https://rpc.ankr.com/eth_sepolia1', NULL, NULL),
    #         ('https://rpc.ankr.com/eth_sepolia2', NULL, NULL),
    #         ('https://rpc.ankr.com/eth_sepolia3', NULL, NULL)
    # ''')

    # ==== END OF TESTS ====

init_db()

# ------------------------#
#     Utility Functions   #
# ------------------------#
def is_member(username: str) -> bool:
    """Checks if a username is a member."""
    cursor.execute('SELECT 1 FROM members WHERE LOWER(username) = ?', (username.lower(),))
    return cursor.fetchone() is not None

# ------------------------#
#      Command Handlers   #
# ------------------------#
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    await update.message.reply_text('Welcome! You are authorized to use this bot. Use /getrpcurl to receive your RPC URL. Use /getsandboxurl to receive your sandbox URL.')

async def get_rpc_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /getrpcurl command."""
    # Get username from update
    username = update.message.chat.username.lower()
    if not username:
        await update.message.reply_text('Please set a username to receive your RPC URL.')
        return

    # Check if username has an RPC URL
    cursor.execute('SELECT url FROM urls WHERE handle = ?', (username,))
    result = cursor.fetchone()
    if result:
        await update.message.reply_text(f'Your RPC URL: {result[0]}')
        return

    # Get the first unassigned RPC URL
    cursor.execute('''
        SELECT id, url FROM urls
        WHERE assigned_at IS NULL
        ORDER BY id ASC
        LIMIT 1
    ''')
    result = cursor.fetchone()

    if result:
        url_id, rpc_url = result
        try:
            cursor.execute('''
                UPDATE urls
                SET handle = ?, assigned_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (username, url_id))
            conn.commit()
            await update.message.reply_text(f'Your RPC URL: {rpc_url}')
            logger.info("Assigned RPC URL %s to user %s", rpc_url, username)
        except sqlite3.Error as e:
            logger.error("Database error: %s", e)
            await update.message.reply_text('Error assigning RPC URL. Please try again.')
    else:
        logger.warning("No unassigned RPC URLs available")
        await update.message.reply_text('No RPC URLs available at the moment. Please try again later.')

async def get_sandbox_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /getsandboxurl command."""
    await update.message.reply_text('Start coding with our web IDE: https://explore.nil.foundation/sandbox/31edd8e9eb48ade662a04a610c0d69fb13a387c49fe283551b42f1c9ca2d3fbe')

# ------------------------#
#           Main          #
# ------------------------#
def main():
    """Starts the bot."""
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getrpcurl", get_rpc_url))
    app.add_handler(CommandHandler("getsandboxurl", get_sandbox_url))

    # Start the bot
    app.run_polling()
    logger.info("Bot started polling.")

if __name__ == '__main__':
    main()
