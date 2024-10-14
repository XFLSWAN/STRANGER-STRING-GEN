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

ask_ques = "**☞︎︎︎ ᴄʜᴏᴏsᴇ ᴏɴᴇ ᴛʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ 𖤍 ✔️ **"
buttons_ques = [
    [
        InlineKeyboardButton("▪️ᴘʏʀᴏɢʀᴀᴍ▪️", callback_data="pyrogram"),
        InlineKeyboardButton("▪️ᴘʏʀᴏɢʀᴀᴍ ᴠ2▪️", callback_data="pyrogram"),
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
async def main(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))


async def generate_session(bot: Client, msg: Message, telethon=False, old_pyro: bool = False, is_bot: bool = False):
    try:
        if telethon:
            ty = "𝖳𝖤𝖫𝖤𝖳𝖧𝖮𝖭"
        else:
            ty = "𝖯𝖸𝖱𝖮𝖦𝖱𝖠𝖬"
            if not old_pyro:
                ty += " 𝖵2"
        if is_bot:
            ty += " 𝖡𝖮𝖳"

        await msg.reply(f"» ᴛʀʏɪɴɢ ᴛᴏ sᴛᴀʀᴛ **{ty}** sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ...")
        user_id = msg.chat.id
        api_id_msg = await bot.ask(user_id, "ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ **ᴀᴘɪ_ɪᴅ** ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ.", filters=filters.text)

        if await cancelled(api_id_msg):
            return

        api_id = int(api_id_msg.text) if api_id_msg.text != "/skip" else config.API_ID
        api_hash = config.API_HASH if api_id_msg.text == "/skip" else (await bot.ask(user_id, "☞︎︎︎ ɴᴏᴡ ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ **ᴀᴘɪ_ʜᴀsʜ** ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.", filters=filters.text)).text

        phone_number_msg = await bot.ask(user_id, "Please enter your phone number or bot token.", filters=filters.text)
        if await cancelled(phone_number_msg):
            return

        phone_number = phone_number_msg.text
        client = await initiate_client(telethon, is_bot, old_pyro, api_id, api_hash, phone_number)

        await handle_authentication(bot, client, msg, user_id, telethon, is_bot, phone_number)
        await send_session_info(bot, client, msg, telethon, ty)

    except Exception as e:
        await msg.reply(f"An error occurred during the session generation: {str(e)}. Please try again.", reply_markup=InlineKeyboardMarkup(gen_button))


async def initiate_client(telethon, is_bot, old_pyro, api_id, api_hash, phone_number):
    if telethon and is_bot:
        return TelegramClient(StringSession(), api_id, api_hash)
    elif telethon:
        return TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        return Client(name="bot", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
    elif old_pyro:
        return Client1(":memory:", api_id=api_id, api_hash=api_hash)
    else:
        return Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)


async def handle_authentication(bot, client, msg, user_id, telethon, is_bot, phone_number):
    if not is_bot:
        code = await client.send_code(phone_number) if not telethon else await client.send_code_request(phone_number)
        phone_code_msg = await bot.ask(user_id, "Send the OTP received.", filters=filters.text)
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    else:
        await client.sign_in_bot(phone_number)


async def send_session_info(bot, client, msg, telethon, ty):
    string_session = client.session.save() if telethon else await client.export_session_string()
    text = f"Your {ty} session has been generated successfully."
    await client.send_message("me", text) if not is_bot else bot.send_message(msg.chat.id, text)
    await client.disconnect()
    await bot.send_message(msg.chat.id, f"Session successfully generated. Check your saved messages.")
