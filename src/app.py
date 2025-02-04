from quart import Quart, render_template, request
from bot import BotManager
from config import Config
from hypercorn.config import Config as HyperConfig
from hypercorn.asyncio import serve
import asyncio

app = Quart(__name__)
bot_manager = None

def init_bot():
    global bot_manager
    bot_manager = BotManager()

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/api/login', methods=['POST'])
async def login():
    try:
        data = await request.get_json()
        phone = data.get('phone', Config.PHONE_NUMBER)
        await bot_manager.start_login(phone)
        return {'status': 'Code sent'}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/verify', methods=['POST'])
async def verify():
    try:
        data = await request.get_json()
        code = data.get('code')
        if not code:
            return {'error': 'Code required'}, 400
        await bot_manager.verify_code(code)
        return {'status': 'Bot started'}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/status')
async def status():
    return {'running': bot_manager.is_running()}

if __name__ == '__main__':
    init_bot()
    config = HyperConfig()
    config.bind = ["0.0.0.0:5000"]
    asyncio.run(serve(app, config))