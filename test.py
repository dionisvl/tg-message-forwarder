import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.custom import Button
from dotenv import load_dotenv
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class TelegramBot:
    def __init__(self):
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.bot_token = os.getenv('BOT_TOKEN')
        self.group_id = int(os.getenv('SOURCE_GROUP_ID'))
        self.client = None
        self.message_text = '''
Order Sum: 7777777777
'''

    async def init_client(self):
        try:
            # Try to load existing session
            session_str = ''
            if os.path.exists('sessions/session_bot.txt'):
                logger.info('Using existing session')
                with open('sessions/session_bot.txt', 'r') as f:
                    session_str = f.read().strip()

            # Initialize client with StringSession
            self.client = TelegramClient(
                StringSession(session_str),
                self.api_id,
                self.api_hash
            )

            # Connect and handle callbacks
            await self.client.connect()

            # Check if we need to sign in
            if not await self.client.is_user_authorized():
                logger.info('Starting bot authorization...')
                await self.client.sign_in(bot_token=self.bot_token)

                # Save session
                with open('sessions/session_bot.txt', 'w') as f:
                    f.write(self.client.session.save())
                logger.info('Bot authorized successfully')

            # Set up callback handler
            @self.client.on(events.CallbackQuery())
            async def callback(event):
                if event.data == b'take_order':
                    await event.answer('Order taken!')
                    # Retrieve the original message
                    original_msg = await event.get_message()
                    await self.client.send_message(
                        self.group_id,
                        f"{original_msg.text}\n✅ Order taken by {event.sender.first_name}!"
                    )
            return True

        except Exception as e:
            logger.error(f'Error initializing client: {e}')
            return False

    async def send_message(self):
        if not self.client:
            logger.error('Client not initialized')
            return

        try:
            message_text = self.message_text
            button = [[Button.inline('Забрать заказ', b'take_order')]]
            await self.client.send_message(
                self.group_id,
                message_text,
                buttons=button
            )
            logger.info('Test message sent successfully')
        except Exception as e:
            logger.error(f'Error sending message: {e}')

    async def run(self):
        if not os.path.exists('sessions'):
            os.makedirs('sessions')

        if await self.init_client():
            await self.send_message()
            await self.client.run_until_disconnected()
        else:
            logger.error('Failed to initialize client')

def main():
    if not os.path.exists('.env'):
        logger.error('.env not exists!!!')
        return

    bot = TelegramBot()
    asyncio.run(bot.run())

if __name__ == '__main__':
    main()