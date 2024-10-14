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

ask_ques = "**☞︎︎︎ Choose the session you want to generate:**"
buttons_ques = [
    [
        InlineKeyboardButton("▪️Pyrogram▪️", callback_data="pyrogram"),
        InlineKeyboardButton("▪️Pyrogram V2▪️", callback_data="pyrogram"),
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
    if old_pyro:
        session_type += " V2"
    if is_bot:
        session_type += " Bot"

    await msg.reply(f"» Starting **{session_type}** session generator...")
    user_id = msg.chat.id

    # Ask for API ID
    api_id_msg = await bot.ask(user_id, "Please send your **API_ID** to proceed.\n\nClick /skip to use the bot API.", filters=filters.text)
    if await cancelled(api_id_msg):
        return

    if api_id_msg.text == "/skip":
        api_id = config.API_ID
        api_hash = config.API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("**API_ID** must be an integer. Please start generating your session again.", reply_markup=InlineKeyboardMarkup(gen_button))
            return
        # Ask for API Hash
        api_hash_msg = await bot.ask(user_id, "Please send your **API_HASH** to continue.", filters=filters.text)
        if await cancelled(api_hash_msg):
            return
        api_hash = api_hash_msg.text

    # Handle phone number or bot token
    prompt = "Enter your phone number in international format to proceed:" if not is_bot else "Send your **bot token** to continue."
    phone_number_msg = await bot.ask(user_id, prompt, filters=filters.text)
    if await cancelled(phone_number_msg):
        return
    phone_number = phone_number_msg.text

    # Create the appropriate client instance based on parameters
    client = await create_client(api_id, api_hash, phone_number, telethon, is_bot, old_pyro)

    if not client:
        await msg.reply("Failed to create client. Please check your API details and try again.", reply_markup=InlineKeyboardMarkup(gen_button))
        return

    # Handle login for user or bot accounts
    await handle_login(client, bot, msg, user_id, phone_number, telethon, is_bot)

async def create_client(api_id, api_hash, phone_number, telethon, is_bot, old_pyro):
    try:
        if telethon:
            return TelegramClient(StringSession(), api_id, api_hash)
        elif is_bot:
            return Client(name="bot", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
        elif old_pyro:
            return Client1(":memory:", api_id=api_id, api_hash=api_hash)
        else:
            return Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    except Exception as e:
        print(f"Error creating client: {e}")
        return None

async def handle_login(client, bot, msg, user_id, phone_number, telethon, is_bot):
    try:
        await client.connect()
        if not is_bot:
            if telethon:
                await client.send_code_request(phone_number)
            else:
                await client.send_code(phone_number)
        else:
            await client.start(bot_token=phone_number)

        await msg.reply("Session successfully generated!", reply_markup=InlineKeyboardMarkup(gen_button))
    except Exception as e:
        await msg.reply(f"An error occurred during session generation: {e}", reply_markup=InlineKeyboardMarkup(gen_button))

async def cancelled(msg):
    if "/cancel" in msg.text or "/restart" in msg.text:
        await msg.reply("**Cancelled the session generation process.**", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
        return True
    return False
