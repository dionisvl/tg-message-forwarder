# Telegram Message Forwarder
Blazing fast and secure message forwarder for Telegram groups.
Built for performance and reliability while keeping the codebase clean and maintainable. Ideal for automated message monitoring and forwarding in private Telegram groups.

### Features

* Monitors group messages using user account session
* Instantly forwards messages with "Test" button
* Database-driven excluded keywords management
* Web-based admin panel for configuration
* Containerized with Docker for easy deployment
* Secure credential management
* Minimal memory footprint

### Tech Stack
* Python 3.12
* Telethon 
* Quart (async web framework)
* PostgreSQL 17
* Docker Compose


## Installation
```
apt-get update
apt-get install git make
curl -fsSL https://get.docker.com | sudo bash
git clone <repo>
cp .env.example .env
# ! Fill in your credentials !
make up
```
- put restart.sh to cron, for every night at 3:00 AM  
  - it's important:
```
chmod +x /home/tgbot/restart.sh
crontab -e
0 3 * * * /home/tgbot/restart.sh >> /home/tgbot/logs/restart.log 2>&1
```
- click admin panel http://127.0.0.1:5000/


### Getting needed envs

1. Getting API_ID and API_HASH:  
      •	Go to my.telegram.org  
      •	Login with your Telegram account  
      •	Select "API development tools"  
      •	Create a new application (App title and Short name can be anything)  
      •	After creation, you'll receive API_ID (numbers) and API_HASH (alphanumeric)
2. Getting Group ID (SOURCE_GROUP_ID) (Web)
    •	Open web.telegram.org  
    •	Go to target group  
    •	Check URL: web.telegram.org/k/#-XXXXXXXXX  
    •	ID is the number after # (including minus)  

3. Getting your USER ID (TARGET_USER_ID):  
      •	Message @userinfobot  
      •	It will automatically reply  
      •	Look for "Id: XXXXXXXXX" in the first line - this is your TARGET_USER_ID  

#### Getting BOTs data:
1. Getting BOT_TOKEN:
   •	Find @BotFather in Telegram  
   •	Send him /newbot  
   •	Choose a name for your bot  
   •	Choose a username (must end with 'bot')  
   •	BotFather will give you the bot token - a long string of letters and numbers
2. Getting Group ID (SOURCE_GROUP_ID) By BOT:  
      •	Add @RawDataBot to your target group  
      •	The bot will send group information  
      •	Look for "Chat ID" field - this is your SOURCE_GROUP_ID  
      •	Remove @RawDataBot from the group after getting the ID  

### Venv
- python3.12 -m venv venv
- bash
- source venv/bin/activate / source venv/bin/activate.fish
- pip install -r requirements.txt

### Crontab
- crontab -e
- @reboot cd /home/tgbot/tg-message-forwarder && make up

## API Endpoints

### Excluded Keywords Management

#### GET /api/excluded_keywords
Returns list of all excluded keywords.

**Response:**
```json
{
  "keywords": ["keyword1", "keyword2", "keyword3"]
}
```

#### POST /api/excluded_keywords
Adds a new excluded keyword.

**Request:**
```json
{
  "keyword": "new_keyword"
}
```

**Response:**
```json
{
  "message": "Keyword added successfully"
}
```

#### DELETE /api/excluded_keywords/{keyword}
Removes an excluded keyword.

**Response:**
```json
{
  "message": "Keyword removed successfully"
}
```

### Database Configuration

The PostgreSQL database is accessible externally via the configured port (default 5433).

**Environment Variables:**
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password  
- `DB_HOST` - Database host (postgres for docker-compose)
- `DB_PORT` - External database port
- `DB_NAME` - Database name (tgbot)

**External Access:**
```bash
psql -h your-server-ip -p 5433 -U tgbot_user -d tgbot
```


### Tools
python tools/get_user_id.py user