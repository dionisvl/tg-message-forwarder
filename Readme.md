# Telegram Message Forwarder
Blazing fast and secure message forwarder for Telegram groups.
Built for performance and reliability while keeping the codebase clean and maintainable. Ideal for automated message monitoring and forwarding in private Telegram groups.

### Features

* Monitors group messages using user account session
* Instantly forwards messages with "Test" button
* Containerized with Docker for easy deployment
* Secure credential management
* Minimal memory footprint

### Tech Stack
* Python 3.12
* Telethon 
* Flask
* Docker Compose


## Installation
```
git clone <repo>
cp .env.example .env
# ! Fill in your credentials !
make up
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
