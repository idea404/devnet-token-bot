# Telegram Bot for RPC URL Distribution

## Features

- Distribute RPC URLs to users based on their Telegram username
- Provide a sandbox URL for web IDE access
- Logging of bot activities

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
- `/getrpcurl`: Receive your assigned RPC URL
- `/getsandboxurl`: Get the URL for the web IDE sandbox
