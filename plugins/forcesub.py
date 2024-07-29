import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import ADMINS, FORCE_MSG
from database.database import fsub, req_db
from bot import Bot
from helpers_func import subscribed, requested

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = []
    
    bot_id = client.me.id
    fsub_entry = await fsub.find_one({"_id": "force_sub_channels"})
    req_db_entry = await req_db.find_one({"_id": "request_channels"})

    fsub_channels = fsub_entry["channel_ids"] if fsub_entry and "channel_ids" in fsub_entry else []
    req_db_channels = req_db_entry["channel_ids"] if req_db_entry and "channel_ids" in req_db_entry else []
    
    # Iterate through each force subscription channel
    for idx, force_sub_channel in enumerate(fsub_channels, start=1):
        if not await subscribed(None, client, message):
            try:
                invite_link = await client.create_chat_invite_link(chat_id=force_sub_channel)
                buttons.append(
                    InlineKeyboardButton(
                        f"Join Channel {idx}",
                        url=invite_link.invite_link
                    )
                )
            except Exception as e:
                print(f"Error creating invite link for channel {force_sub_channel}: {e}")

    # Iterate through each request subscription channel
    for idx, request_channel in enumerate(req_db_channels, start=len(fsub_channels)+1):
        if not await requested(None, client, message):
            try:
                invite_link = await client.create_chat_invite_link(chat_id=request_channel, creates_join_request=True)
                buttons.append(
                    InlineKeyboardButton(
                        f"Request Channel {idx}",
                        url=invite_link.invite_link
                    )
                )
            except Exception as e:
                print(f"Error creating invite link for channel {request_channel}: {e}")

    # Group buttons into rows of two
    button_rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    try:
        button_rows.append(
            [
                InlineKeyboardButton(
                    text='Try Again',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(button_rows),
        quote=True,
        disable_web_page_preview=True
    )

# Add fsub in db 
@Bot.on_message(filters.command('addfsub') & filters.private & filters.user(ADMINS))
async def add_fsub(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to add as fsub in the bot. If adding more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]
    bot_id = client.me.id

    for channel_id in channel_ids:
        try:
            print(channel_id)
            test_msg = await client.send_message(int(channel_id), "test")
            await test_msg.delete()
        except:
            await message.reply(f"Please make admin bot in channel_id: {channel_id} or double-check the ID.")
            return

    await add_force_sub_channel(int(channel_id))
    await message.reply(f"Added channel IDs: {', '.join(channel_ids)}")

### Deleting Channel IDs
@Bot.on_message(filters.command('delfsub') & filters.private & filters.user(ADMINS))
async def del_fsub(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to delete from fsub in the bot. If deleting more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]
    bot_id = client.me.id

    for channel_id in channel_ids:
        await remove_force_sub_channel(int(channel_id))

    await message.reply(f"Deleted channel IDs: {', '.join(channel_ids)}")

### Showing All Channel IDs
@Bot.on_message(filters.command('showfsub') & filters.private & filters.user(ADMINS))
async def show_fsub(client, message):
    bot_id = client.me.id
    fsub_entry = await fsub.find_one({"_id": "force_sub_channels"})

    if fsub_entry and "channel_ids" in fsub_entry:
        channel_ids = fsub_entry["channel_ids"]
        channel_info = []
        for channel_id in channel_ids:
            chat = await client.get_chat(int(channel_id))
            channel_info.append(f"→ **[{chat.title}]({chat.invite_link})**")
        if channel_info:
            await message.reply(f"**Force Subscribed channels:**\n" + "\n".join(channel_info), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        else:
            await message.reply("No subscribed channels found.")
    else:
        await message.reply("No subscribed channel IDs found.")

# Add IDs in db
@Bot.on_message(filters.command('addreq') & filters.private & filters.user(ADMINS))
async def add_req(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to add. If adding more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]

    added_channels = []
    for channel_id in channel_ids:
        try:
            test_msg = await client.send_message(int(channel_id), "test")
            await test_msg.delete()
            await add_request_channel(int(channel_id))
            added_channels.append(channel_id)
        except Exception as e:
            await message.reply(f"Please make the bot an admin in channel ID: {channel_id} or double-check the ID. Error: {e}")
            return

    if added_channels:
        await message.reply(f"Added channel IDs: {', '.join(added_channels)}")

# Deleting Channel IDs
@Bot.on_message(filters.command('delreq') & filters.private & filters.user(ADMINS))
async def del_req(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to delete from fsub in the bot. If deleting more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]

    deleted_channels = []
    for channel_id in channel_ids:
        try:
            await remove_request_channel(int(channel_id))
            deleted_channels.append(channel_id)
        except Exception as e:
            await message.reply(f"Error deleting channel ID: {channel_id}. Error: {e}")

    if deleted_channels:
        await message.reply(f"Deleted channel IDs: {', '.join(deleted_channels)}")

### Show Request Channels
@Bot.on_message(filters.command('showreq') & filters.private & filters.user(ADMINS))
async def show_req(client, message):
    bot_id = client.me.id
    req_db_entry = await req_db.find_one({"_id": "request_channels"})

    if req_db_entry and "channel_ids" in req_db_entry:
        channel_ids = req_db_entry["channel_ids"]
        channel_info = []
        for channel_id in channel_ids:
            chat = await client.get_chat(int(channel_id))
            channel_info.append(f"→ **[{chat.title}]({chat.invite_link})**")
        if channel_info:
            await message.reply(f"**Request channels:**\n" + "\n".join(channel_info), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        else:
            await message.reply("No request channels found.")
    else:
        await message.reply("No request channel IDs found.")
