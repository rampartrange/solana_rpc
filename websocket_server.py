import asyncio
import websockets
import json
import random
import time
import logging
import sys


logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Stream logs to stdout
    ]
)

logger = logging.getLogger(__name__)

websocket_connections = set()


async def register(websocket):
    logger.info('register event received')
    websocket_connections.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        websocket_connections.remove(websocket)


async def send_messages():
    while True:
        message_type = random.choice(["INVOKE", "NOTHING", "ERROR"])
        message = {
            "type": message_type,
            "timestamp": int(time.time() * 1000),
            "payload": {"data": f"Sample data for {message_type}"}
        }
        message_json = json.dumps(message)
        websockets.broadcast(websocket_connections, message_json)
        logger.info(f"Sent: {message}")
        await asyncio.sleep(random.uniform(3, 6))  # Send a message every 1 to 3 seconds


async def main():
    async with websockets.serve(register, "0.0.0.0", 9000):
        logger.info("Server started")
        await send_messages()


if __name__ == "__main__":
    logger.info("Server started")
    asyncio.run(main())
