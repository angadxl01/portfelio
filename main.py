from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Initialization (Apne credentials dalein)
app = Client(
    "dms_forward_bot",
    api_id="36645562",
    api_hash=ccad405579d80b82492abbf4a7777907",
    bot_token="8794925442:AAFIHaUAJM8ZXt2guEN7Lq2kKyTTKzECWqw"
)

# Aapke select kiye hue buttons ka Menu layout
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Mass DM Campaign", callback_data="start_campaign")],
        [InlineKeyboardButton("✍️ Set Message", callback_data="set_message")],
        [
            InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
            InlineKeyboardButton("👤 My Account", callback_data="my_account")
        ],
        [
            InlineKeyboardButton("⭐ Go VIP Premium", callback_data="vip_premium"),
            InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem_code")
        ],
        [
            InlineKeyboardButton("➕ Add Account", callback_data="add_account"),
            InlineKeyboardButton("💰 Refer & Earn", callback_data="refer_earn")
        ],
        [InlineKeyboardButton("❓ How to Use", callback_data="how_to_use")]
    ])

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    text = (
        "**DMS FORWARD BOT**\n\n"
        "Welcome! Please choose an option below:"
    )
    await message.reply_text(text, reply_markup=get_main_menu())

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
