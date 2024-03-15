import asyncio
import json
from datetime import datetime
import websockets
import uuid

clients = set()
messages = {}

async def echo(websocket, path):
    clients.add(websocket)
    try:
        load_messages()

        for message in messages.values():
            await websocket.send(json.dumps(message))
        
        async for message in websocket:
            if message == "get_users_count":
                await websocket.send(f"users_count:{len(clients)}")
            else:
                message_with_name = f"[{datetime.now()}] {message}"
                print(message_with_name)
                message_id = str(uuid.uuid4()) 
                messages[message_id] = {
                    "sender": "Server",
                    "message": message_with_name
                }
                for client in clients:
                    await client.send(json.dumps(messages[message_id]))
                    
                save_messages()
    finally:
        clients.remove(websocket)

def save_messages():
    with open("messages.json", "w") as file:
        json.dump(messages, file)

def load_messages():
    try:
        with open("messages.json", "r") as file:
            global messages
            messages = json.load(file)
    except FileNotFoundError:
        pass

async def main():
    server = await websockets.serve(echo, "10.0.0.44", 8765)
    await server.wait_closed()

asyncio.run(main())

