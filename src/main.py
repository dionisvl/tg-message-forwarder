from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import sys
from config import Config
from utils import is_message_processed, mark_message_processed

async def get_string_session():
    async with TelegramClient(StringSession(), Config.API_ID, Config.API_HASH) as client:
        await client.start(phone=Config.PHONE_NUMBER)
        return client.session.save()

async def main():
    try:
        with open('sessions/session.txt', 'r') as f:
            session_str = f.read().strip()
    except FileNotFoundError:
        if not sys.stdin.isatty():
            print("No session found and running in non-interactive mode")
            sys.exit(1)

        session_str = await get_string_session()
        with open('sessions/session.txt', 'w') as f:
            f.write(session_str)

    client = TelegramClient(StringSession(session_str), Config.API_ID, Config.API_HASH)

    @client.on(events.NewMessage(chats=Config.SOURCE_GROUP_ID))
    async def forward_message(event):
        if is_message_processed(event.message.id):
            return

        if any(button.text == "Тест" for row in (event.message.reply_markup.rows if event.message.reply_markup else [])
               for button in row.buttons):
            try:
                await client.forward_messages(Config.TARGET_USER_ID, event.message)
                mark_message_processed(event.message.id)
            except Exception as e:
                print(f"Error forwarding message {event.message.id}: {str(e)}")

    async with client:
        print("Bot started successfully!")
        await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
