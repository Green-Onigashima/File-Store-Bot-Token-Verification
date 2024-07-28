import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS, FORCE_MSG
from database.database import fsub, req_db


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = []

    bot_id = client.me.id

    # Fetch forced subscription channels
    fsub_entry = fsub.find_one({"_id": bot_id})
    if fsub_entry and "channel_ids" in fsub_entry:
        force_sub_channels = fsub_entry["channel_ids"]
    else:
        force_sub_channels = []

    # Fetch join request channels
    join_req_channels = req_db.find({})

    # Create buttons for forced subscription channels
    for idx, force_sub_channel in enumerate(force_sub_channels, start=1):
        try:
            invite_link = await client.create_chat_invite_link(chat_id=force_sub_channel)
            buttons.append(
                InlineKeyboardButton(
                    f"Join FSub Channel {idx}",
                    url=invite_link.invite_link
                )
            )
        except Exception as e:
            print(f"Error creating invite link for fsub channel {force_sub_channel}: {e}")

    # Create buttons for join request channels
    for idx, entry in enumerate(join_req_channels, start=1):
        channel_id = entry["_id"]
        try:
            chat = await client.get_chat(int(channel_id))
            buttons.append(
                InlineKeyboardButton(
                    f"Join Request Channel {idx}",
                    url=chat.invite_link
                )
            )
        except Exception as e:
            print(f"Error getting chat info for join request channel {channel_id}: {e}")

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

    invalid_ids = []
    for channel_id in channel_ids:
        try:
            channel_id_int = int(channel_id)
            test_msg = await client.send_message(channel_id_int, "test")
            await test_msg.delete()
            fsub.update_one(
                {"_id": bot_id},
                {"$addToSet": {"channel_ids": channel_id_int}},
                upsert=True
            )
        except ValueError:
            invalid_ids.append(channel_id)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception as e:
            print(f"Error adding channel ID {channel_id}: {e}")
            invalid_ids.append(channel_id)

    if invalid_ids:
        await message.reply(f"Invalid channel IDs or errors occurred: {', '.join(invalid_ids)}")
    else:
        await message.reply(f"Added channel IDs: {', '.join(channel_ids)}")


# Deleting Channel IDs
@Bot.on_message(filters.command('delfsub') & filters.private & filters.user(ADMINS))
async def del_fsub(client, message):
    if len(message.command) == 1:
        await message.reply("Please provide channel IDs to delete from fsub in the bot. If deleting more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]
    bot_id = client.me.id

    fsub.update_one(
        {"_id": bot_id},
        {"$pull": {"channel_ids": {"$in": channel_ids}}}
    )
    await message.reply(f"Deleted channel IDs: {', '.join(channel_ids)}")


# Showing All Channel IDs
@Bot.on_message(filters.command('showfsub') & filters.private & filters.user(ADMINS))
async def show_fsub(client, message):
    bot_id = client.me.id
    fsub_entry = fsub.find_one({"_id": bot_id})

    if fsub_entry and "channel_ids" in fsub_entry:
        channel_ids = fsub_entry["channel_ids"]
        channel_info = []
        for channel_id in channel_ids:
            try:
                chat = await client.get_chat(int(channel_id))
                channel_info.append(f"→ **[{chat.title}]({chat.invite_link})**")
            except Exception as e:
                channel_info.append(f"→ **Channel ID: {channel_id}** (Error: {e})")
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
            channel_id_int = int(channel_id)
            test_msg = await client.send_message(channel_id_int, "test")
            await test_msg.delete()
            req_db.update_one({"_id": channel_id_int}, {"$set": {"_id": channel_id_int}}, upsert=True)
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
        await message.reply("Please provide channel IDs to delete from the request database. If deleting more than one, separate IDs with spaces.")
        return

    channel_ids = message.text.split()[1:]
    deleted_channels = []
    for channel_id in channel_ids:
        try:
            result = req_db.delete_one({"_id": int(channel_id)})
            if result.deleted_count > 0:
                deleted_channels.append(channel_id)
            else:
                await message.reply(f"Channel ID: {channel_id} not found in the database. Please double-check the ID.")
        except Exception as e:
            await message.reply(f"Error deleting channel ID: {channel_id}. Error: {e}")

    if deleted_channels:
        await message.reply(f"Deleted channel IDs: {', '.join(deleted_channels)}")


# Showing All Channel IDs
@Bot.on_message(filters.command('showreq') & filters.private & filters.user(ADMINS))
async def show_req(client, message):
    req_entries = req_db.find({})

    channel_info = []
    for entry in req_entries:
        channel_id = entry["_id"]
        user_count = len(entry.get("User_INFO", []))
        try:
            chat = await client.get_chat(int(channel_id))
            channel_info.append(f"→ **[{chat.title}]({chat.invite_link})**: {user_count} user requests")
        except Exception as e:
            channel_info.append(f"→ **Channel ID: {channel_id}**: {user_count} users (Error: {e})")

    if channel_info:
        await message.reply(f"**Channels Added For Request Count:**\n" + "\n".join(channel_info), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
        await message.reply("No channels found.")


@Bot.on_chat_join_request()
async def join_reqs(client, join_req: ChatJoinRequest):
    channel_id = join_req.chat.id
    
    if req_db.find_one({"_id": channel_id}):
        user_data = {
            "user_id": join_req.from_user.id,
            "first_name": join_req.from_user.first_name,
            "username": join_req.from_user.username,
            "date": join_req.date
        }

        # Update USER_INFO in db
        req_db.update_one(
            {"_id": channel_id},
            {"$push": {"User_INFO": user_data}},
            upsert=True
        )


# Resetting User_INFO for a Channel ID
@Bot.on_message(filters.command('rreset') & filters.private & filters.user(ADMINS))
async def reset_req(client, message):
    if len(message.command) != 2:
        await message.reply("Please provide a single channel ID to reset user info.")
        return

    channel_id = message.text.split()[1]
    try:
        result = req_db.update_one({"_id": int(channel_id)}, {"$unset": {"User_INFO": ""}})
        if result.modified_count > 0:
            await message.reply(f"User info reset for channel ID: {channel_id}")
        else:
            await message.reply(f"Channel ID: {channel_id} not found in the database. Please double-check the ID.")
    except Exception as e:
        await message.reply(f"Error resetting user info for channel ID: {channel_id}. Error: {e}")
