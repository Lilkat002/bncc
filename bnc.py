import time
import json
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *

# Set the lookback period for calculating Bollinger Bands
LOOKBACK_PERIOD = 20

# Set the stop loss and take profit levels for each trade
STOP_LOSS_PERCENTAGE = 0.995
TAKE_PROFIT_PERCENTAGE = 1.005

# Set the Binance API key and secret
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

# Create a Binance client
client = Client(api_key=API_KEY, api_secret=API_SECRET)

# Subscribe to the trade stream for the specified symbol
def subscribe_to_trades(symbol):
    bm = BinanceSocketManager(client)
    conn_key = bm.start_trade_socket(symbol=symbol, callback=callback)

    bm.start()

# Callback function for trade stream
def callback(msg):
    # Calculate Bollinger Bands using the standard deviation of the close price over the lookback period
    prices = [float(x["p"]) for x in msg]
    sma = sum(prices[-LOOKBACK_PERIOD:]) / LOOKBACK_PERIOD
    stdev = (sum([(x - sma) ** 2 for x in prices[-LOOKBACK_PERIOD:]]) / LOOKBACK_PERIOD) ** 0.5
    upper_band = sma + 2 * stdev
    lower_band = sma - 2 * stdev
    
    # Get the current price
    current_price = float(msg[-1]["p"])
    
    # Check if the market is consolidating or if a breakout has occurred
    is_consolidating = lower_band <= current_price <= upper_band
    is_breakout = current_price < lower_band or current_price > upper_band
    
    # If the market is consolidating, don't open any new trades
    if is_consolidating:
        return
    
     # If a breakout occurs, enter a long position if the price is breaking out to the upside, or a short position if the price is breaking out to the downside
    if is_breakout:
        if current_price > upper_band:
            # Calculate the stop loss and take profit levels
            stop_loss = current_price * STOP_LOSS_PERCENTAGE
            take_profit = current_price * TAKE_PROFIT_PERCENTAGE
            # Place a long order
            client.order_market_buy(symbol=symbol, quantity=1)
            # Set the stop loss and take profit levels for the trade
            client.order_oco(symbol=symbol, stop_client_order_id="stop", limit_client_order_id="limit", stop_price=stop_loss, limit_price=take_profit)
        elif current_price < lower_band:
            # Calculate the stop loss and take profit levels
            stop_loss = current_price * (2 - STOP_LOSS_PERCENTAGE)
            take_profit = current_price * (2 - TAKE_PROFIT_PERCENTAGE)
            # Place a short order
            client.order_market_sell(symbol=symbol, quantity=1)
            # Set the stop loss and take profit levels for the trade
            client.order_oco(symbol=symbol, stop_client_order_id="stop", limit_client_order_id="limit", stop_price=stop_loss, limit_price=take_profit)

def main():
    # Set the symbol to trade
    symbol = "BTCUSDT"
    
    # Subscribe to the trade stream
    subscribe_to_trades(symbol)
    
    # Keep the script running indefinitely
    while True:
        time.sleep(1)

# Run the main function
if __name__ == "__main__":
    main()
