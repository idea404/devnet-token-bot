import logging
import sqlite3
from dotenv import load_dotenv
import os
from functools import wraps
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

# Initialize database tables
def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            email TEXT,
            handle TEXT,
            assigned_at TIMESTAMP DEFAULT NULL
        )
    ''')
    # add Xidea404 to members if not already there
    cursor.execute('SELECT 1 FROM members WHERE LOWER(username) = ?', ("xidea404",))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO members (username) VALUES (?)', ("xidea404",))
    conn.commit()

init_db()

# ------------------------#
#     Utility Functions   #
# ------------------------#
def is_member(username: str) -> bool:
    """Checks if a username is a member."""
    cursor.execute('SELECT 1 FROM members WHERE LOWER(username) = ?', (username.lower(),))
    return cursor.fetchone() is not None

# ------------------------#
#      Decorators         #
# ------------------------#
def restricted(func):
    """Decorator to restrict access to member users based on Telegram handle."""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user.username:
            logger.warning("User ID %s does not have a username.", user.id)
            await update.message.reply_text("You need to set a Telegram username to use this bot.")
            return
        if not is_member(user.username):
            logger.warning("Unauthorized access denied for user ID %s (username: %s).", user.id, user.username)
            await update.message.reply_text("You are not authorized to use this bot.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

# ------------------------#
#      Command Handlers   #
# ------------------------#
@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    await update.message.reply_text('Welcome! You are authorized to use this bot. Use /gettoken to receive your RPC URL. Use /addmember to add a =nil; TG user to members.')

@restricted
async def addmember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /addmember command."""
    args = context.args

    if len(args) != 1:
        await update.message.reply_text('Usage: /addmember <nil_team_member_tg_handle>')
        return

    username = args[0]
    username = username.replace("@", "").lower()

    # Check if the user is already a member
    cursor.execute('SELECT 1 FROM members WHERE LOWER(username) = ?', (username,))
    if cursor.fetchone():
        await update.message.reply_text(f'{username} is already a member.')
        return

    # Add the user as a member
    try:
        cursor.execute('INSERT INTO members (username) VALUES (?)', (username,))
        conn.commit()
        await update.message.reply_text(f'{username} added to members.')
    except sqlite3.Error as e:
        logger.error("Database error: %s", e)
        await update.message.reply_text('Error adding user to members. Please try again.')

@restricted
async def gettoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /gettoken command."""
    args = context.args

    if len(args) != 1:
        await update.message.reply_text('Usage: /gettoken <developer_email_or_tg_handle>')
        return

    user_input = args[0]

    # Determine if the user input is an email or a handle
    handle = None
    email = None
    if user_input[0] == "@" or "@" not in user_input:
        handle = user_input.replace("@", "").lower()
    else:
        email = user_input

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
                SET handle = ?, email = ?, assigned_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (handle, email, url_id))
            conn.commit()
            await update.message.reply_text(f'{rpc_url}')
            logger.info("Assigned RPC URL %s to user %s", rpc_url, handle)
        except sqlite3.Error as e:
            logger.error("Database error: %s", e)
            await update.message.reply_text('Error assigning RPC URL. Please try again.')
    else:
        logger.warning("No unassigned RPC URLs available")
        await update.message.reply_text('No RPC URLs available at the moment. Please try again later.')

# ------------------------#
#           Main          #
# ------------------------#
def main():
    """Starts the bot."""
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addmember", addmember))
    app.add_handler(CommandHandler("gettoken", gettoken))

    # Start the bot
    app.run_polling()
    logger.info("Bot started polling.")

if __name__ == '__main__':
    main()
