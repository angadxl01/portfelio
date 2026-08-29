import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, filters

API_ID = 36645562
API_HASH = "ccad405579d80b82492abbf4a7777907"
BOT_TOKEN = "8822648253:AAGZroIwI4F7udtFlhABotrsqjAXm_qcSq4"
ADMIN_ID = 8895089247

app = Client(
    "dms_forward_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text("🤖 Bot is working perfectly!")

if __name__ == "__main__":
    print("Bot starting...")
    app.run()
