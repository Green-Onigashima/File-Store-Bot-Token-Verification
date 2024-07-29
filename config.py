import os
import logging
from operator import add
from os import environ, getenv
from logging.handlers import RotatingFileHandler

#import dotenv
#dotenv.load_dotenv()




TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "6105757517:AAHS2KgJDLuEErCoLyxkfOjCYwUhOZSvnlY") 
APP_ID = int(os.environ.get("APP_ID", "25695562"))
API_HASH = os.environ.get("API_HASH", "0b691c3e86603a7e34aae0b5927d725a")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1001732352061"))
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/+CT5g4kpXx-tlN2I1")
OWNER_ID = int(os.environ.get("OWNER_ID", "1895952308"))
PORT = os.environ.get("PORT", "8080")
DB_URL = os.environ.get("DB_URL", "")
DB_NAME = os.environ.get("DB_NAME", "Cluster0")

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))
START_MSG = os.environ.get("START_MESSAGE", "<blockquote><b>Hello {mention}\n\nI can store private files in Specified Channel and other users can access it from special link.")
OWNER_TAG = os.environ.get("OWNER_TAG", "StupidBoi69")
TIME = int(os.environ.get("TIME", "60"))

#USE_PAYMENT = True if (os.environ.get("USE_PAYMENT", "FALSE") == "TRUE") & (USE_SHORTLINK) else False

PAYMENT_LOGS = int(environ.get('PAYMENT_LOGS', '-1001968254468'))
SHORTLINK_API_URL = os.environ.get("SHORTLINK_API_URL", "modijiurl.com")
SHORTLINK_API_KEY = os.environ.get("SHORTLINK_API_KEY", "a0c51b7b2b16924757c1e2eb6ca27096f9df7208")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', "43200"))
TUT_VID = os.environ.get("TUT_VID", "https://t.me/Anime_Elixir/12")
UPI_USERNAME = os.environ.get("UPI_USERNAME", "StupidBoi69")



START_MSG = os.environ.get("START_MESSAGE", "<blockquote><b>ℹ️ Hello {mention}\nI can store private files in Specified Channel and other users can access it from special link. 💾</b></blockquote>")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "<blockquote><b>ℹ️ Hello {mention}\nYou need to join in my Channel to use me\nKindly Please join Channel</b></blockquote>")

BOT_STATS_TEXT = "<b>BOT UPTIME {uptime}</b>"
USER_REPLY_TEXT = "<blockquote><b>🔴 Don't send me messages directly I'm only File Share bot!\nTo resolve any issues contact bot developer: @StupidBoi69</b></blockquote>"

CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)
PROTECT_CONTENT = os.environ.get("PROTECT_CONTENT", "False")
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", "True")
USE_PAYMENT = os.environ.get("USE_PAYMENT", "True")
USE_SHORTLINK = os.environ.get('USE_SHORTLINK', "True")

try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "1895952308").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")
ADMINS = []
ADMINS.append(OWNER_ID)


try:
    PREMIUM_USERS=[]
    for x in (os.environ.get("PREMIUM_USERS", "1895952308").split()):
        PREMIUM_USERS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")
PREMIUM_USERS = []
PREMIUM_USERS.append(ADMINS)


LOG_FILE_NAME = "logs.txt"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
