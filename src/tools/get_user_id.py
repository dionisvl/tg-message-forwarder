#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from telegram_factory import TelegramClientFactory
from session_manager import SessionManager

async def get_user_id(username):
    session_str = SessionManager.load_session('user')
    if not session_str:
        print("Error: No session found")
        return
    
    client = await TelegramClientFactory.create_client(session_str)
    
    try:
        user = await client.get_entity(username.lstrip('@'))
        print(user.id)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python get_user_id.py <username>")
        sys.exit(1)
    
    asyncio.run(get_user_id(sys.argv[1]))