from quart import Quart, render_template, request
from bot import BotManager
from config import Config
from hypercorn.config import Config as HyperConfig
from hypercorn.asyncio import serve
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Quart(__name__)
bot_manager = None

async def init_app():
    global bot_manager
    config = HyperConfig()
    config.bind = ["0.0.0.0:5000"]

    # Initialize bot manager first
    bot_manager = BotManager()
    # Try to start existing session
    await bot_manager.start_existing_session()

    # Start the web server
    await serve(app, config)

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/api/login', methods=['POST'])
async def login():
    try:
        data = await request.get_json()
        phone = data.get('phone', Config.PHONE_NUMBER)
        logger.info(f"Starting login process for phone: {phone}")
        await bot_manager.start_login(phone)
        return {'status': 'Code sent'}
    except Exception as e:
        logger.error(f"Login error: {e}")
        return {'error': str(e)}, 500

@app.route('/api/verify', methods=['POST'])
async def verify():
    try:
        data = await request.get_json()
        code = data.get('code')
        if not code:
            logger.error("Verification error: Code required")
            return {'error': 'Code required'}, 400
        logger.info("Attempting to verify code...")
        await bot_manager.verify_code(code)
        return {'status': 'Bot started'}
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return {'error': str(e)}, 500

@app.route('/api/toggle_monitoring', methods=['POST'])
async def toggle_monitoring():
    try:
        if not bot_manager.is_running():
            return {'error': 'Bot is not running'}, 400

        is_monitoring = await bot_manager.toggle_monitoring()
        return {'status': 'Monitoring ' + ('started' if is_monitoring else 'stopped')}
    except Exception as e:
        logger.error(f"Toggle monitoring error: {e}")
        return {'error': str(e)}, 500

@app.route('/api/status')
async def status():
    return {
        'running': bot_manager.is_running(),
        'monitoring': bot_manager.is_monitoring()
    }

if __name__ == '__main__':
    asyncio.run(init_app())