IBKR Telegram Bot
A Python-based trading bot for Interactive Brokers (IBKR) paper trading, controlled via Telegram. Execute market buy/sell orders with take-profit and stop-loss, and modify orders seamlessly.
Features

Market Orders: Place buy/sell orders at market prices (/buy, /sell).
Bracket Orders: Set take-profit/stop-loss for buy orders.
Order Modification: Update orders with /replace.
Help: View usage with /help.

Prerequisites

Python 3.8+
IBKR TWS (paper trading, port 7497)
Telegram bot token and chat ID

Installation

Clone Repository:git clone https://github.com/jahanzaib-codes/ibkr-telegram-bot.git
cd ibkr-telegram-bot


Install Dependencies:pip install -r requirements.txt


Configure TWS:
Open TWS, log in to paper trading account.
Go to File > Global Configuration > API > Settings:
Enable ActiveX and Socket Clients.
Set port to 7497.
Add 127.0.0.1 to Trusted IPs.




Verify Telegram Config:
In bot.py, ensure:TELEGRAM_TOKEN = "8175293763:AAEECMe9YOJErWjz3AnM9KbhZINchU-_aZg"
CHAT_ID = "1798492490"




Run Bot:python bot.py



Usage

Buy: /buy <symbol> <quantity> <take_profit> <stop_loss>
Example: /buy AAPL 10 150.50 140.25


Sell: /sell <symbol> <quantity>
Example: /sell AAPL 10


Replace: /replace <symbol> <order_id> <new_take_profit> <new_stop_loss>
Example: /replace AAPL 12345 155.00 135.00


Help: /help for detailed guide.

Troubleshooting

Connection Issues: Verify TWS is running, port 7497 is open, and 127.0.0.1 is trusted.
Order Rejections: Check symbol, account balance, or market hours.
Logs: Review console for errors.

Notes

For IBKR paper trading only (port 7497).
Test thoroughly to avoid errors.

License
MIT License
Disclaimer
For educational use in IBKR demo account. Trading involves risk. Test before live use.
