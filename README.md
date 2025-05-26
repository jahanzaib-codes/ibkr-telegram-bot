# IBKR Telegram Bot

<p align="center">
  <strong>Trade stocks via Telegram on IBKR's paper trading account</strong>
</p>

A Python-based bot for Interactive Brokers (IBKR) demo account, enabling market buy/sell orders with take-profit and stop-loss via Telegram commands.

## Features
- <b>Market Orders</b>: Execute buy/sell orders at market prices.
- <b>Bracket Orders</b>: Set take-profit/stop-loss for buy orders.
- <b>Order Modification</b>: Update orders with ease.
- <b>Help</b>: Detailed usage guide via <code>/help</code>.

## Prerequisites
<ul>
  <li>Python 3.8+</li>
  <li>IBKR TWS (paper trading, port 7497)</li>
  <li>Telegram bot token and chat ID</li>
</ul>

## Installation
1. <b>Clone Repository</b>:
   ```bash
   git clone https://github.com/jahanzaib-codes/ibkr-telegram-bot.git
   cd ibkr-telegram-bot
   ```

2. <b>Install Dependencies</b>:
   ```bash
   pip install -r requirements.txt
   ```

3. <b>Configure TWS</b>:
   <ul>
     <li>Open TWS, log in to paper trading account.</li>
     <li>Go to <code>File > Global Configuration > API > Settings</code>:
       <ul>
         <li>Enable <code>ActiveX and Socket Clients</code>.</li>
         <li>Set port to <code>7497</code>.</li>
         <li>Add <code>127.0.0.1</code> to Trusted IPs.</li>
       </ul>
     </li>
   </ul>

4. <b>Configure Telegram</b>:
   <ul>
     <li>Update <code>bot.py</code> with your Telegram bot token and chat ID.</li>
     <li>Get token from <code>@BotFather</code> and chat ID from <code>@userinfobot</code>.</li>
   </ul>

5. <b>Run Bot</b>:
   ```bash
   python bot.py
   ```

## Usage
Use these Telegram commands:
<ul>
  <li><b>/buy &lt;symbol&gt; &lt;quantity&gt; &lt;take_profit&gt; &lt;stop_loss&gt;</b>
    <p>Example: <code>/buy AAPL 10 150.50 140.25</code><br>
    Buys 10 AAPL shares at market price, sets take-profit at $150.50, stop-loss at $140.25.</p>
  </li>
  <li><b>/sell &lt;symbol&gt; &lt;quantity&gt;</b>
    <p>Example: <code>/sell AAPL 10</code><br>
    Sells 10 AAPL shares at market price.</p>
  </li>
  <li><b>/replace &lt;symbol&gt; &lt;order_id&gt; &lt;new_take_profit&gt; &lt;new_stop_loss&gt;</b>
    <p>Example: <code>/replace AAPL 12345 155.00 135.00</code><br>
    Updates order ID 12345 for AAPL with take-profit at $155.00, stop-loss at $135.00.</p>
  </li>
  <li><b>/help</b>
    <p>Shows detailed usage guide.</p>
  </li>
</ul>

## Troubleshooting
<ul>
  <li><b>Connection Issues</b>: Ensure TWS is running, port 7497 is open, and <code>127.0.0.1</code> is trusted.</li>
  <li><b>Order Rejections</b>: Verify symbol, account balance, and market hours.</li>
  <li><b>Logs</b>: Check console for error details.</li>
</ul>

## Notes
<ul>
  <li>For IBKR paper trading (port 7497).</li>
  <li>Test thoroughly to avoid errors.</li>
</ul>

## License
MIT License

## Disclaimer
For educational use in IBKR demo account. Trading involves risk. Test before live use.
