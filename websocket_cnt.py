import asyncio
import websockets
import json

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
    spot_symbol = "btcusdt"  # Replace with your desired spot symbol
    future_symbol = "btcusdt"  # Replace with your desired future symbol
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            listen_spot(spot_symbol),
            listen_future(future_symbol)
        )
    )
