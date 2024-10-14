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
from pyrogram.errors import (
    ApiIdInvalid as ApiIdInvalid1,
    PhoneNumberInvalid as PhoneNumberInvalid1,
    PhoneCodeInvalid as PhoneCodeInvalid1,
    PhoneCodeExpired as PhoneCodeExpired1,
    SessionPasswordNeeded as SessionPasswordNeeded1,
    PasswordHashInvalid as PasswordHashInvalid1
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

ask_ques = "**☞︎︎︎ Choose one that you want to generate a session:**"
buttons_ques = [
    [
        InlineKeyboardButton("▪️Pyrogram▪️", callback_data="pyrogram"),
        InlineKeyboardButton("▪️Pyrogram V2▪️", callback_data="pyrogram_v2"),
    ],
    [
        InlineKeyboardButton("🔺Telethon🔺", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("🔸Pyrogram Bot🔸", callback_data="pyrogram_bot"),
        InlineKeyboardButton("🔹Telethon Bot🔹", callback_data="telethon_bot"),
    ],
]

gen_button = [
    [
        InlineKeyboardButton(text="🔹Generate Session🔹", callback_data="generate")
    ]
]

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["generate", "gen", "string", "str"]))
async def main(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))

async def generate_session(bot: Client, msg: Message, telethon=False, old_pyro: bool = False, is_bot: bool = False):
    session_type = "Telethon" if telethon else "Pyrogram"
    if is_bot:
        session_type += " Bot"
    
    await msg.reply(f"Starting {session_type} session generation...")

    user_id = msg.chat.id
    api_id_msg = await bot.ask(user_id, "Please send your API_ID to proceed.\n\nClick on /skip to use default Bot API.", filters=filters.text)
    if await cancelled(api_id_msg):
        return

    if api_id_msg.text == "/skip":
        api_id = config.API_ID
        api_hash = config.API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("API_ID must be an integer. Restart the generation process.", reply_markup=InlineKeyboardMarkup(gen_button))
            return

        api_hash_msg = await bot.ask(user_id, "Now send your API_HASH to continue.", filters=filters.text)
        if await cancelled(api_hash_msg):
            return
        api_hash = api_hash_msg.text

    prompt_message = "Please enter your phone number (Example: +91 95xxxxxxXX)" if not is_bot else "Please send your Bot Token (Example: 12345:ABCDE)"
    phone_number_msg = await bot.ask(user_id, prompt_message, filters=filters.text)
    if await cancelled(phone_number_msg):
        return
    phone_number = phone_number_msg.text

    await msg.reply("Attempting to login...")

    # Configure the client object based on conditions
    if telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        client = Client(name="bot", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
    else:
        client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)

    await client.connect()

    # Bot sessions are not saved to the user's direct messages
    if is_bot:
        session_string = await client.export_session_string()
        await bot.send_message(msg.chat.id, f"Here is your bot session string:\n\n`{session_string}`")
    else:
        session_string = await client.export_session_string()
        try:
            await client.send_message("me", f"Your session string is:\n\n`{session_string}`\n\nPlease do not share it.")
        except Exception as e:
            await msg.reply("Session generated successfully but could not save to direct messages.", reply_markup=InlineKeyboardMarkup(gen_button))

    await client.disconnect()
    await bot.send_message(msg.chat.id, "Session generation complete. Please check your saved messages.")

async def cancelled(msg):
    if "/cancel" in msg.text or msg.text.startswith("/"):
        await msg.reply("Process cancelled.", reply_markup=InlineKeyboardMarkup(gen_button))
        return True
    return False
