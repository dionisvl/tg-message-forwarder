from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
from config import Config
from utils import is_message_processed, mark_message_processed

# Using string session for better persistence
client = TelegramClient('sessions/user_session', Config.API_ID, Config.API_HASH)

@client.on(events.NewMessage(chats=Config.SOURCE_GROUP_ID))
async def forward_message(event):
    """Forward new messages from source group to target user"""
    if is_message_processed(event.message.id):
        return

    # Check if message has "Test" button
    if any(button.text == "Тест" for row in (event.message.reply_markup.rows if event.message.reply_markup else [])
           for button in row.buttons):
        try:
            await client.forward_messages(
                Config.TARGET_USER_ID,
                event.message
            )
            mark_message_processed(event.message.id)
        except Exception as e:
            print(f"Error forwarding message {event.message.id}: {str(e)}")

async def main():
    """Start the client and handle authentication"""
    # Connect to Telegram
    await client.start(phone=Config.PHONE_NUMBER)

    # Ensure you're connected
    if await client.is_user_authorized():
        print("Successfully authenticated!")
    else:
        print("Authentication failed!")
        return

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
