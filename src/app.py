import os
import logging
import asyncio
from typing import Optional

from quart import Quart, render_template, request, session, redirect, url_for
from bot import BotManager
from config import Config
from hypercorn.config import Config as HyperConfig
from hypercorn.asyncio import serve

# Create logs directory if not exists and add a file handler for logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- SET UP FILE HANDLER ---
file_handler = logging.FileHandler('logs/app.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logging.getLogger().addHandler(file_handler)

app = Quart(__name__)
app.secret_key = os.getenv('ADMIN_SECRET', 'default_secret')  # Secret key for session management
bot_manager: Optional[BotManager] = None

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

# Admin login route (GET & POST)
@app.route('/admin/login', methods=['GET', 'POST'])
async def admin_login():
    if request.method == 'POST':
        form = await request.form
        password = form.get('password')
        if password == os.getenv('ADMIN_PASSWORD'):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid password", 403
    return await render_template('admin_login.html')

# Logout route for admin panel
@app.route('/admin/logout')
async def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

# Protected index route: if not logged in, redirect to login page
@app.route('/')
async def index():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    # Pass the connection interval for log refresh to the template
    return await render_template('index.html', connection_interval=Config.CONNECTION_CHECK_INTERVAL)

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

        logger.info(f"Monitoring toggled to: {is_monitoring}")

        return {'status': 'Monitoring ' + ('started' if is_monitoring else 'stopped')}
    except Exception as e:
        logger.error(f"Toggle monitoring error: {e}")
        return {'error': str(e)}, 500

@app.route('/api/status')
async def status():
    return {
        'running': bot_manager.is_running(),
        'monitoring': bot_manager.is_monitoring(),
        'session_lost': bot_manager.is_session_lost()
    }

# Serve application logs from the log file
@app.route('/api/logs')
async def get_logs():
    try:
        with open('logs/app.log', 'r') as f:
            log_data = f.read()
        return {'logs': log_data}
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    asyncio.run(init_app())
