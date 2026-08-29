from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# --- Flask Web Server (Render ke liye zaroori hai) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is alive and running!"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

# --- Telegram Bot Configuration ---
# Apni asli details yahan daalein
API_ID = 36645562  # Apna api_id number mein
API_HASH = "ccad405579d80b82492abbf4a7777907"
BOT_TOKEN = "8822648253:AAGZroIwI4F7udtFlhABotrsqjAXm_qcSq4"

app = Client(
    "dms_forward_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

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
    # Web server ko alag thread mein chalayein
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Bot and Web Server are running...")
    app.run()
