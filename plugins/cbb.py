from pyrogram import __version__
from bot import Bot
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import *

# Callback query handler
@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    
    # About section
    if data == "about":
        await query.message.edit_text(
            text = f"""<blockquote><b>📯 Hi {query.from_user.mention}, I'm file sharing bot, Created by @StupidBoi69.\n</b></blockquote>""",
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📴 Close", callback_data="close")]
                ]
            )
        )
    
    # Close message
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
    
    # Buy Premium section
    elif data == "buy_prem":
        await query.message.edit_text(
            text=f"<blockquote><b>⏺️ Hello {query.from_user.username}
            
<u>💰 Premium Membership Plans</u>

↪️ ₹49 rs For 7 Days
↪️ ₹149 rs For 1 Month
↪️ ₹349 rs For 3 Months
👛 UPI ID : https://graph.org/file/fd1487021734ee86c78b4.jpg

<u>➕ How to purchase premium membership</u>

#Step_1) Pay the amount according to your favourite plan to UPI ID. ⤴️
#Step_2) Send payment screenshot to the bot then reply the screenshot with /bought command. 📸
#Step_3) Your Premium membership plan will activate after verifying your purchase. 🛂</b></blockquote>""",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📸 Send Payment Screenshot", url = f"https//t.me/{UPI_USERNAME}")],
                    [InlineKeyboardButton("📴 Close", callback_data="close")]
                ]
            )
        )

# Command handler for /bought
@Client.on_message(filters.command("bought") & filters.private)
async def bought(client, message):
    # Reply to the user indicating that the payment is being checked
    msg = await message.reply("**🕵️ Have patience i'm checking...**")
    
    replyed = message.reply_to_message
    
    # Check if there's a reply with a screenshot
    if not replyed:
        await msg.edit(
            "<blockquote><b>Please reply with the screenshot of your payment for the premium purchase to proceed.\n\n"
            "For example, first upload your screenshot, then reply to it using the /bought command</b></blockquote>"
        )
    if replyed and replyed.photo:
        # Send the payment screenshot to Owner
        await client.send_photo(
            photo=replyed.photo.file_id,
            chat_id=PAYMENT_LOGS,
            caption=(
                f"<blockquote><b>Hi @{UPI_USERNAME}\nPlease verify {message.from_user.mention}'s payment.\n\n"
                f"User Link: <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n"
                f"Username: {message.from_user.username} - {message.from_user.id}\n</b></blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📴 Close", callback_data="close_data")]
                ]
            )
        )
        await msg.edit_text("<blockquote>📠 Your screenshot has been sent to Owner. Have patience till payment verification...</b></blockquote>")
