from pyrogram.types import Message
from telethon import TelegramClient
from pyrogram import Client, filters
from pyrogram import Client as Client1
from asyncio.exceptions import TimeoutError
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)

import config

ask_ques = "**☞︎︎︎ ᴄʜᴏᴏsᴇ ᴏɴᴇ ᴛʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ 𖤍 ✔️ **"
buttons_ques = [
    [
        InlineKeyboardButton("▪️ᴘʏʀᴏɢʀᴀᴍ▪️", callback_data="pyrogram"),
        InlineKeyboardButton("▪️ᴘʏʀᴏɢʀᴀᴍ ᴠ2▪️", callback_data="pyrogram_v2"),
    ],
    [
        InlineKeyboardButton("🔺ᴛᴇʟᴇᴛʜᴏɴ🔺", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("🔸ᴘʏʀᴏɢʀᴀᴍ ʙᴏᴛ🔸", callback_data="pyrogram_bot"),
        InlineKeyboardButton("🔹ᴛᴇʟᴇᴛʜᴏɴ ʙᴏᴛ🔹", callback_data="telethon_bot"),
    ],
]

gen_button = [
    [
        InlineKeyboardButton(text="🔹ɢᴇɴʀᴀᴛᴇ sᴇssɪᴏɴ🔹", callback_data="generate")
    ]
]

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["generate", "gen", "string", "str"]))
async def main(_, msg: Message):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))

async def generate_session(bot: Client, msg: Message, telethon=False, old_pyro: bool = False, is_bot: bool = False):
    ty = "𝖳𝖤𝖫𝖤𝖳𝖧𝖮𝖭" if telethon else "𝖯𝖸𝖱𝖮𝖦𝖱𝖠𝖬"
    if not old_pyro:
        ty += " 𝖵2"
    if is_bot:
        ty += " 𝖡𝖮𝖳"

    await msg.reply(f"» ᴛʀʏɪɴɢ ᴛᴏ sᴛᴀʀᴛ **{ty}** sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ...")
    user_id = msg.chat.id

    api_id_msg = await bot.ask(user_id, "ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ **ᴀᴘɪ_ɪᴅ** ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ.\n\nᴄʟɪᴄᴋ ᴏɴ /skip 𝖥ᴏʀ ᴜsɪɴɢ ʙᴏᴛ ᴀᴘɪ.", filters=filters.text)
    if await cancelled(api_id_msg):
        return

    if api_id_msg.text == "/skip":
        api_id = config.API_ID
        api_hash = config.API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("**𝖠𝖯𝖨_𝖨𝖣** ᴍᴜsᴛ ʙᴇ ᴀɴ ɪɴᴛᴇɢᴇʀ. Please try again.", reply_markup=InlineKeyboardMarkup(gen_button))
            return

        api_hash_msg = await bot.ask(user_id, "Please send your **API_HASH** to continue.", filters=filters.text)
        if await cancelled(api_hash_msg):
            return
        api_hash = api_hash_msg.text

    t = "Enter your phone number (e.g., `+91 95xxxxxxXX`) to proceed:" if not is_bot else "Send your bot token to continue."
    phone_number_msg = await bot.ask(user_id, t, filters=filters.text)
    if await cancelled(phone_number_msg):
        return

    phone_number = phone_number_msg.text
    if not is_bot:
        await msg.reply("Attempting to send OTP to the provided number...")

    # Initialize the appropriate client
    client = initialize_client(api_id, api_hash, phone_number, telethon, is_bot, old_pyro)

    # Handle session generation process
    session = await handle_session_creation(client, bot, msg, phone_number, telethon, is_bot)
    if session:
        await send_session_to_user(client, bot, msg, session, telethon, is_bot)

async def cancelled(msg):
    if msg.text.lower() in ["/cancel", "/restart"]:
        await msg.reply("Cancelled the ongoing string generation process.", reply_markup=InlineKeyboardMarkup(gen_button))
        return True
    return False
