# Telegram Bot for RPC URL Distribution

## Features

- Restricted access: Only authorized members can use the bot
- Existing members can add new members to the authorized list
- Distribute RPC URLs to new users based on their email or Telegram handle

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the root directory and add your Telegram Bot Token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. Initialize the database:
   The database will be automatically initialized when you run the bot for the first time.

## Running the Bot

To start the bot, run:

```
python bot.py
```

## Usage

- `/start`: Start the bot and receive instructions
- `/addmember`: Add your email or Telegram handle to the authorized list
- `/gettoken`: Receive the RPC URL based on your email or Telegram handle
