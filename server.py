import asyncio
import websockets

async def echo(websocket):  # Remove 'path' argument
    print("Client connected")
    try:
        while True:
            message = await websocket.recv()  # Receive a message from the client
            print(f"Received: {message}")
            await websocket.send(f"Echo: {message}")  # Echo the message back to the client
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

async def main():
    # No 'path' parameter is passed to the handler
    async with websockets.serve(echo, "localhost", 8765):
        print("WebSocket server running at ws://localhost:8765")
        await asyncio.Future()  # Keep the server running forever

if __name__ == "__main__":
    asyncio.run(main())
