import asyncio
import logging
from ib_insync import IB, Stock, MarketOrder, LimitOrder, StopOrder
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uuid

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# IBKR and Telegram configuration
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"  # Replace with your Telegram bot token
CHAT_ID = "YOUR_CHAT_ID"  # Replace with your Telegram chat ID
IBKR_PORT = 7497  # Paper trading port
MAX_RETRIES = 3
CLIENT_ID_RANGE = range(1, 11)  # Try client IDs 1 to 10

class TradingBot:
    def __init__(self):
        self.ib = IB()
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        self.connected = False

    async def connect_ibkr(self):
        """Connect to IBKR TWS or Gateway with retry and dynamic client ID"""
        for client_id in CLIENT_ID_RANGE:
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    logger.info(f"Attempting to connect with clientId {client_id}, attempt {attempt}/{MAX_RETRIES}")
                    await self.ib.connectAsync('127.0.0.1', IBKR_PORT, clientId=client_id, timeout=5)
                    self.connected = True
                    logger.info(f"Connected to IBKR with clientId {client_id}")
                    return
                except Exception as e:
                    logger.warning(f"Connection attempt {attempt} failed with clientId {client_id}: {e}")
                    if attempt == MAX_RETRIES:
                        logger.error(f"Max retries reached for clientId {client_id}")
                    await asyncio.sleep(1)
        raise Exception("Failed to connect to IBKR after trying all client IDs")

    async def disconnect_ibkr(self):
        """Disconnect from IBKR"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IBKR")

    async def place_bracket_order(self, symbol, quantity, take_profit, stop_loss, action='BUY'):
        """Place a bracket order with market price and take-profit/stop-loss"""
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            contracts = await self.ib.qualifyContractsAsync(contract)
            if not contracts:
                return f"Invalid symbol: {symbol}. Check if the stock ticker is correct."
            
            # Create market order
            parent = MarketOrder(action=action, totalQuantity=quantity)
            parent.orderId = self.ib.client.getReqId()
            
            # Create take-profit and stop-loss orders
            take_profit_order = LimitOrder(
                action='SELL' if action == 'BUY' else 'BUY',
                totalQuantity=quantity,
                lmtPrice=take_profit,
                parentId=parent.orderId,
                transmit=False
            )
            stop_loss_order = StopOrder(
                action='SELL' if action == 'BUY' else 'BUY',
                totalQuantity=quantity,
                stopPrice=stop_loss,
                parentId=parent.orderId,
                transmit=True
            )
            
            # Place orders
            trades = [self.ib.placeOrder(contract, order) for order in [parent, take_profit_order, stop_loss_order]]
            for trade in trades:
                if trade.orderStatus.status == 'Rejected':
                    return f"Order rejected: {trade.log[-1].message}"
            return f"{action} order placed for {quantity} shares of {symbol} at market price with TP {take_profit} and SL {stop_loss}"
        except Exception as e:
            logger.error(f"Error placing order for {symbol}: {e}")
            return f"Error placing order: {e}"

    async def replace_order(self, symbol, order_id, new_take_profit, new_stop_loss):
        """Replace take-profit and stop-loss of an existing order"""
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            contracts = await self.ib.qualifyContractsAsync(contract)
            if not contracts:
                return f"Invalid symbol: {symbol}. Check if the stock ticker is correct."
            
            # Fetch open orders
            orders = self.ib.openOrders()
            target_order = None
            for order in orders:
                if order.orderId == order_id and order.contract.symbol == symbol:
                    target_order = order
                    break
            
            if not target_order:
                return f"No order found with ID {order_id} for {symbol}"

            # Modify take-profit and stop-loss
            target_order.lmtPrice = new_take_profit
            target_order.stopPrice = new_stop_loss
            trade = self.ib.placeOrder(contract, target_order)
            if trade.orderStatus.status == 'Rejected':
                return f"Order modification rejected: {trade.log[-1].message}"
            return f"Order {order_id} for {symbol} updated with TP {new_take_profit} and SL {new_stop_loss}"
        except Exception as e:
            logger.error(f"Error replacing order for {symbol}: {e}")
            return f"Error replacing order: {e}"

    async def start(self):
        """Start the bot and Telegram handlers"""
        try:
            await self.connect_ibkr()
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            return
        
        # Telegram command handlers
        self.app.add_handler(CommandHandler("buy", self.buy_command))
        self.app.add_handler(CommandHandler("sell", self.sell_command))
        self.app.add_handler(CommandHandler("replace", self.replace_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("Telegram bot started")

    async def stop(self):
        """Stop the bot"""
        await self.app.stop()
        await self.disconnect_ibkr()
        logger.info("Bot stopped")

    async def buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /buy command: /buy <symbol> <quantity> <take_profit> <stop_loss>"""
        if str(update.message.chat_id) != CHAT_ID:
            await update.message.reply_text("Unauthorized access")
            return
        
        try:
            args = context.args
            if len(args) != 4:
                await update.message.reply_text("Usage: /buy <symbol> <quantity> <take_profit> <stop_loss>")
                return
            
            symbol, quantity, take_profit, stop_loss = args
            quantity = int(quantity)
            take_profit = float(take_profit)
            stop_loss = float(stop_loss)
            
            result = await self.place_bracket_order(symbol, quantity, take_profit, stop_loss, action='BUY')
            await update.message.reply_text(result)
        except Exception as e:
            logger.error(f"Error in buy command: {e}")
            await update.message.reply_text(f"Error: {e}")

    async def sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sell command: /sell <symbol> <quantity>"""
        if str(update.message.chat_id) != CHAT_ID:
            await update.message.reply_text("Unauthorized access")
            return
        
        try:
            args = context.args
            if len(args) != 2:
                await update.message.reply_text("Usage: /sell <symbol> <quantity>")
                return
            
            symbol, quantity = args
            quantity = int(quantity)
            
            result = await self.place_bracket_order(symbol, quantity, 0, 0, action='SELL')
            await update.message.reply_text(result)
        except Exception as e:
            logger.error(f"Error in sell command: {e}")
            await update.message.reply_text(f"Error: {e}")

    async def replace_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /replace command: /replace <symbol> <order_id> <new_take_profit> <new_stop_loss>"""
        if str(update.message.chat_id) != CHAT_ID:
            await update.message.reply_text("Unauthorized access")
            return
        
        try:
            args = context.args
            if len(args) != 4:
                await update.message.reply_text("Usage: /replace <symbol> <order_id> <new_take_profit> <new_stop_loss>")
                return
            
            symbol, order_id, new_take_profit, new_stop_loss = args
            order_id = int(order_id)
            new_take_profit = float(new_take_profit)
            new_stop_loss = float(new_stop_loss)
            
            result = await self.replace_order(symbol, order_id, new_take_profit, new_stop_loss)
            await update.message.reply_text(result)
        except Exception as e:
            logger.error(f"Error in replace command: {e}")
            await update.message.reply_text(f"Error: {e}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command with detailed usage"""
        if str(update.message.chat_id) != CHAT_ID:
            await update.message.reply_text("Unauthorized access")
            return
        
        help_text = """
Trading Bot Usage Guide:
This bot allows you to trade stocks on Interactive Brokers (IBKR) demo account via Telegram commands. Ensure IBKR TWS is running with API access enabled on port 7497.

**Commands**:
1. **/buy <symbol> <quantity> <take_profit> <stop_loss>**
   - Places a market buy order with take-profit and stop-loss.
   - `<symbol>`: Stock ticker (e.g., AAPL for Apple).
   - `<quantity>`: Number of shares (e.g., 10).
   - `<take_profit>`: Absolute price for take-profit (e.g., 150.50).
   - `<stop_loss>`: Absolute price for stop-loss (e.g., 140.25).
   - Example: `/buy AAPL 10 150.50 140.25`
     - Buys 10 shares of AAPL at market price, sets take-profit at $150.50, stop-loss at $140.25.

2. **/sell <symbol> <quantity>**
   - Places a market sell order for the specified quantity.
   - `<symbol>`: Stock ticker.
   - `<quantity>`: Number of shares.
   - Example: `/sell AAPL 10`
     - Sells 10 shares of AAPL at market price.

3. **/replace <symbol> <order_id> <new_take_profit> <new_stop_loss>**
   - Modifies an existing order’s take-profit and stop-loss.
   - `<symbol>`: Stock ticker.
   - `<order_id>`: Order ID from TWS (check TWS for order ID).
   - `<new_take_profit>`: New absolute take-profit price.
   - `<new_stop_loss>`: New absolute stop-loss price.
   - Example: `/replace AAPL 12345 155.00 135.00`
     - Updates order ID 12345 for AAPL with take-profit at $155.00, stop-loss at $135.00.

4. **/help**
   - Displays this usage guide.

**Setup**:
- Install TWS and enable API access (File > Global Configuration > API > Settings).
- Set port to 7497, add 127.0.0.1 to trusted IPs, enable socket clients.
- Install dependencies: `pip install ib_insync python-telegram-bot`.
- Run the bot: `python bot.py`.
- Use the Telegram bot with your token and chat ID.

**Notes**:
- For demo account only (port 7497).
- Ensure TWS is running before starting the bot.
- Only the authorized chat ID can use commands.
- Check TWS for order IDs when replacing orders.
- Test thoroughly to avoid errors.
"""
        await update.message.reply_text(help_text)

async def main():
    bot = TradingBot()
    try:
        await bot.start()
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await bot.stop()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())