from aiohttp import web
from database.database import full_adminbase
from plugins import web_server
from pyrogram import Client, enums
import sys
from pyromod import listen
from datetime import datetime
from config import *


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

            
    async def start(self):
        try:
            await super().start()
            usr_bot_me = await self.get_me()
            self.username = usr_bot_me.username
            self.namebot = usr_bot_me.first_name
            self.uptime = datetime.now()
            self.LOGGER(__name__).info(
                f"🟢 TG_BOT_TOKEN detected!\nFirst Name: {self.namebot}\nUsername: @{self.username}\n"
            )
        except Exception as a:
            self.LOGGER(__name__).warning(a)
            self.LOGGER(__name__).info("🔴 Bot Stopped.")
            sys.exit()
           
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message", disable_notification=True)
            await test.delete()
            self.LOGGER(__name__).info(
                f"🟢 CHANNEL_ID Database detected!\nTitle: {db_channel.title}\n Chat ID: {db_channel.id}\n"
            )
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"🔴 Make sure @{self.username} is an admin in your DataBase channel, {CHANNEL_ID}"
            )
            self.LOGGER(__name__).info("🔴 Bot Stopped.")
            sys.exit()

        self.set_parse_mode(enums.ParseMode.HTML)
        self.LOGGER(__name__).info(f"""🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢""")
        self.LOGGER(__name__).info("🥵 Bot is Running..!💨")
        self.LOGGER(__name__).info("🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢")

        
        initadmin = await full_adminbase()
        for x in initadmin:
            if x in ADMINS:
                continue
            ADMINS.append(x)
        await self.send_message(
            chat_id=OWNER_ID,
            text="**Bot has started! 😉**"
        )

        
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
