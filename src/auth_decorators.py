from functools import wraps
from quart import session, jsonify

def require_auth(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'error': 'Unauthorized'}), 401
        return await f(*args, **kwargs)
    return decorated_function