from binance.client import Client
from binance.cm_futures import CMFutures
import json
import time
import asyncio
import websockets
import json

api_key = "X5YOXEAJAvbsy57O0RG9y1LZTtfJpHKtBSZu05iDDF1biOryTqp0RXHkIMuXZgcE"
api_secret = "qc6ets7DqAROveLD2YYN3RUtOBZDsOQjNNzJOxxqWE4F0pzGYYl7ky2x7KbVkH00"

spot_client = Client(api_key=api_key, api_secret=api_secret)
future_client = CMFutures(key=api_key, secret=api_secret)
exchange_info = spot_client.get_exchange_info()

def get_symbol_info(symbol):
    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            return s
    return None

def get_tradeable_symbols():
    filter_1_list = []
    for s in exchange_info['symbols']:
        if s['status'] == 'TRADING':
            filter_1_list.append(s['symbol'])
    future_symbol = spot_client.futures_symbol_ticker()
    filter_2_list = []
    for i in future_symbol:
        if i['symbol'] in filter_1_list:
            filter_2_list.append(i['symbol'])
    return filter_2_list

def round_to_tick_size(price, tick_size):
    return round(price / tick_size) * tick_size

def precision_spot_handler(symbol, price, quantity):
    symbol_info = get_symbol_info(symbol)
    if not symbol_info:
        print(f"Symbol {symbol} not found.")
        return None, None

    base_precision = symbol_info['baseAssetPrecision']
    quote_precision = symbol_info['quoteAssetPrecision']

    for f in symbol_info['filters']:
        if f['filterType'] == 'PRICE_FILTER':
            min_price = float(f['minPrice'])
            max_price = float(f['maxPrice'])
            tick_size = float(f['tickSize'])
        if f['filterType'] == 'LOT_SIZE':
            min_qty = float(f['minQty'])
            max_qty = float(f['maxQty'])
            step_size = float(f['stepSize'])

    # Round the taker price to the nearest tick size
    rounded_price = round_to_tick_size(price, tick_size)
    
    # Format the taker price to the allowed precision
    rounded_price = float(format(rounded_price, f'.{quote_precision}f'))
    
    # Ensure the taker price is within the allowed range
    if float(rounded_price) < min_price or float(rounded_price) > max_price:
        print(f"Price {rounded_price} is out of bounds. Adjusting to within [{min_price}, {max_price}]")
        rounded_price = format(max(min(float(rounded_price), max_price), min_price), f'.{quote_precision}f')

    # Round the quantity to the nearest step size
    rounded_quantity = round(quantity / step_size) * step_size

    # Ensure the quantity is within the allowed range
    if rounded_quantity < min_qty or rounded_quantity > max_qty:
        print(f"Quantity {rounded_quantity} is out of bounds. Adjusting to within [{min_qty}, {max_qty}]")
        rounded_quantity = max(min(rounded_quantity, max_qty), min_qty)

    # Format the quantity to the allowed precision
    rounded_quantity = format(rounded_quantity, f'.{base_precision}f')
    return rounded_price, rounded_quantity, base_precision, quote_precision, symbol_info

async def listen_spot(symbol):
    uri = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to spot: {uri}")

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                process_spot_message(data)
            except websockets.ConnectionClosed as e:
                print(f"Spot connection closed: {e}")
                break
            except Exception as e:
                print(f"An error occurred on spot: {e}")
                break

async def listen_future(symbol):
    uri = f"wss://fstream.binance.com/ws/{symbol}@trade"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to future: {uri}")

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                process_future_message(data)
            except websockets.ConnectionClosed as e:
                print(f"Future connection closed: {e}")
                break
            except Exception as e:
                print(f"An error occurred on future: {e}")
                break

def process_spot_message(message):
    # Process the incoming spot message here
    # For example, print the trade data
    print(f"Spot Trade Data: {message}")

def process_future_message(message):
    # Process the incoming future message here
    # For example, print the trade data
    print(f"Future Trade Data: {message}")


if __name__ == "__main__":
    switch = 0
    usdt_quantity = 10
    symbol = 'MATICUSDT'
    future_symbol = ''
    """ Step 1: Get tradeable symbols """
    # tradeable_symbols = get_tradeable_symbols()

    """ Step 2: Manage precision """
    # Manage precision for spot 
    mark_price = float(spot_client.get_symbol_ticker(symbol=symbol)['price'])
    crypto_quantity = usdt_quantity / mark_price
    taker_open_price = mark_price*0.99
    spot_price,spot_quantity, base_precision, quote_precision, symbol_info = precision_spot_handler(symbol, taker_open_price, crypto_quantity)
    float_spot_quantity = float(spot_quantity)
    # Manage precision for future
    future_ex_info = future_client.exchange_info()
    for s in future_ex_info['symbols']:
        if s['baseAsset'] == symbol_info['baseAsset']:
            future_symbol_for_checking = s['symbol']
            future_symbol = symbol_info['symbol']
            print(future_symbol, future_symbol_for_checking)
            symbol_futu_info = s
            quantity_precision = symbol_futu_info["quantityPrecision"]
            price_precision = symbol_futu_info["pricePrecision"]
    # print(precision)
    # print(future_symbol)
    future_quantity = round(float_spot_quantity, quantity_precision)
    future_price_calculated = mark_price * 0.991
    future_price = round(future_price_calculated, price_precision)

    """ Step 3: Create order """
    # # Check spot order status
    
    # # print(spot_order)
    # # print("-----")
    # # print(spot_order_status)
    #             # Create spot order
    # spot_order = spot_client.create_order(
    # symbol=symbol,
    # side='BUY',
    # type='LIMIT',
    # timeInForce='GTC',
    # quantity = spot_quantity,
    # price = spot_price
    # )
    # if spot_order:
    #     print(">>> Spot order created <<<")
    # # Manage precision
    # spot_order_status = spot_client.get_order(symbol=symbol, orderId=spot_order['orderId'])
    # if spot_order_status['status'] == 'FILLED':
        # Post a new order
        # "----"
    future_order = spot_client.futures_create_order(
        symbol=future_symbol,
        side='SELL',
        type='LIMIT',
        timeInForce='GTC',
        quantity = future_quantity,
        price = future_price
    )


    if future_order:
        print(">>> Future order created <<<")
    # #     # If order is filled within 24h, switch to 2
    # #     switch = 2
    # #     print(">>> Future order created <<<")
    # # else:
    # #     switch = 1
    # #     time.sleep(5)
    # #     print("Waiting for spot order to be filled")
            

    # # """ Step 4: Close order"""
    while True:
    #     # Check if order is filled
    #     # spot_order_status = spot_client.get_order(symbol=symbol, orderId=spot_order['orderId'])
    #     # print(spot_order_status)
    #     print("spot",spot_order['status'])
        # if spot_order_status['status'] == 'FILLED':
        #     break
        # # Check if order future is filled
        # future_order_status = future_client.get_orders()
        print("future",future_order['status'], future_order)
        time.sleep(1)
    #     # pass

    # # If spot filled and future not filled, handle future if price go down too high
    # #do something

    # # If future filled and spot not filled, handle spot if price go up too high
    # #do something

    # # If both filled, wait until price change 1%
    # #do something
    # #         spot_symbol = "btcusdt"  # Replace with your desired spot symbol
    # #         future_symbol = "btcusdt"  # Replace with your desired future symbol
    # #         loop = asyncio.get_event_loop()
    # #         loop.run_until_complete(
    # #             asyncio.gather(
    # #                 listen_spot(spot_symbol),
    # #                 listen_future(future_symbol)
    # #             )
    # #         )
    # # while switch == 2:    
    #     #     if future_order['status'] == 'FILLED':
    #     #         # Create another spot order with the future price
    #     #         new_spot_order = spot_client.create_order(
    #     #             symbol=symbol,
    #     #             side='BUY',
    #     #             type='LIMIT',
    #     #             timeInForce='GTC',
    #     #             quantity=spot_quantity,
    #     #             price=future_price
    #     #         )
    #     #         print("Closing market maker")
    #     #         break
                
    #     #     else:
    #     #         switch = 2
    #     #         time.sleep(5)
    #     #         print("Waiting for future order to be filled")
    

    # # """ Step 4: If price go up above 1% integrate with option """

    # """ Step 5: If price go below mark price 1%, execute close order"""
    # # a = future_client.query_order(symbol=future_symbol_for_checking, orderId=order_id)
    # # print(a)
    # # if future_order['status'] == 'FILLED':
    # #     spot_close_order = spot_client.create_order(
    # #     symbol=symbol,
    # #     side='BUY',
    # #     type='LIMIT',
    # #     timeInForce='GTC',
    # #     quantity = spot_quantity,
    # #     price = spot_price
    # #     )
    # # Check future order status
    # # print(future_order)
    # # order_id = future_order['orderId']
    # # origin_client_order_id = future_order['clientOrderId']
    # # future_order_status = future_client.query_order(symbol=future_symbol_for_checking, orderId=order_id, origClientOrderId=origin_client_order_id)
    # # print(future_symbol_for_checking)
    # # print(future_order)
    # # print("-----")
    # # print(future_order_status)
    # # while True:
    # #     if future_order_status['status'] == 'FILLED':
    # #         break

    # # # Taker_close_price = mark_price * 0.99
    # # spot_close_price, spot_close_quantity, base_precision, quote_precision, symbol_info = precision_spot_handler(symbol, future_price, crypto_quantity)

    # # # Tao lenh dat ban
    # # dat_ban = spot_client.create_order(
    # # symbol=symbol,
    # # side='BUY',
    # # type='LIMIT',
    # # timeInForce='GTC',
    # # quantity = spot_quantity,
    # # price = spot_close_price
    # # )


