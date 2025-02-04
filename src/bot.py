from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from config import Config
from utils import is_message_processed, mark_message_processed

class BotManager:
    def __init__(self):
        self.client = None
        self._running = False

    async def start_login(self, phone):
        if not self.client:
            self.client = TelegramClient(StringSession(), Config.API_ID, Config.API_HASH)
            await self.client.connect()
            await self.client.send_code_request(phone)

    async def verify_code(self, code):
        if not self.client:
            raise Exception("Must call start_login first")
        try:
            await self.client.sign_in(code=code)
        except SessionPasswordNeededError:
            await self.client.sign_in(password=Config.PASSWORD_2FA)

        session_str = self.client.session.save()
        with open('sessions/session.txt', 'w') as f:
            f.write(session_str)

        self._running = True

        @self.client.on(events.NewMessage(chats=Config.SOURCE_GROUP_ID))
        async def forward_message(event):
            if is_message_processed(event.message.id):
                return

            if any(button.text == "Тест" for row in (event.message.reply_markup.rows if event.message.reply_markup else [])
                   for button in row.buttons):
                try:
                    await self.client.forward_messages(Config.TARGET_USER_ID, event.message)
                    mark_message_processed(event.message.id)
                except Exception as e:
                    print(f"Error forwarding: {str(e)}")

        await self.client.run_until_disconnected()

    def is_running(self):
        return self._running