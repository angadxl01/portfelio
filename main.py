from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import os
import threading

# ==================== CONFIGURATION ====================
API_ID = 36645562  # Apna numeric api_id daalein
API_HASH = "ccad405579d80b82492abbf4a7777907"
BOT_TOKEN = "8822648253:AAGZroIwI4F7udtFlhABotrsqjAXm_qcSq4"
ADMIN_ID = 8895089247  # ⚠️ Yahan apna Telegram User ID daalein
# =======================================================

# Flask Web Server Setup (Render ke liye port binding)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running live and healthy!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# Pyrogram Bot Client Setup
app = Client(
    "dms_forward_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Global Storage
user_states = {}
temp_join_data = {}
bot_users = set()
saved_accounts = []
saved_channels = []
active_join_configs = {}

def get_main_menu(user_id):
    buttons = [
        [InlineKeyboardButton("🚀 Start Mass DM Campaign", callback_data="start_campaign")],
        [
            InlineKeyboardButton("✍️ Set Message", callback_data="set_message"),
            InlineKeyboardButton("👀 Preview Message", callback_data="preview_message")
        ],
        [
            InlineKeyboardButton("👤 My Account", callback_data="my_account"),
            InlineKeyboardButton("⭐ Go VIP Premium", callback_data="vip_premium")
        ],
        [
            InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem_code"),
            InlineKeyboardButton("➕ Add Account", callback_data="add_account")
        ],
        [
            InlineKeyboardButton("❌ Remove Account", callback_data="remove_account"),
            InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")
        ],
        [
            InlineKeyboardButton("🤝 Join Request DM", callback_data="join_request_dm"),
            InlineKeyboardButton("❓ How to Use", callback_data="how_to_use")
        ],
        [InlineKeyboardButton("🛠️ Support", callback_data="support")]
    ]
    if user_id == ADMIN_ID:
        buttons.insert(0, [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)

def get_admin_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Total Stats", callback_data="admin_stats"),
            InlineKeyboardButton("📢 Broadcast Msg", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton("📂 All Accounts", callback_data="admin_view_accounts"),
            InlineKeyboardButton("📢 All Channels", callback_data="admin_view_channels")
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ])

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user_id = message.from_user.id
    bot_users.add(user_id)
    user_states.pop(user_id, None)
    await message.reply_text(
        "**🤖 DMS FORWARD BOT MENU**\n\nWelcome! Please choose an option below:",
        reply_markup=get_main_menu(user_id)
    )

@app.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin_command_handler(client, message):
    await message.reply_text(
        "**👑 WELCOME TO ADMIN PANEL**",
        reply_markup=get_admin_menu()
    )

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    await callback_query.answer()
    
    if data == "main_menu":
        user_states.pop(user_id, None)
        await callback_query.message.edit_text(
            "**🤖 DMS FORWARD BOT MENU**\n\nWelcome back!",
            reply_markup=get_main_menu(user_id)
        )
    elif data == "admin_panel":
        if user_id != ADMIN_ID: return
        await callback_query.message.edit_text("👑 **ADMIN PANEL**", reply_markup=get_admin_menu())
    elif data == "admin_stats":
        if user_id != ADMIN_ID: return
        stats_text = (
            f"📊 **STATS:**\nUsers: {len(bot_users)}\n"
            f"Accounts: {len(saved_accounts)}\nChannels: {len(saved_channels)}"
        )
        await callback_query.message.edit_text(stats_text, reply_markup=get_admin_menu())
    elif data == "admin_broadcast":
        if user_id != ADMIN_ID: return
        user_states[user_id] = "waiting_for_broadcast"
        await callback_query.message.reply_text("📢 Send broadcast message:")
    elif data == "admin_view_accounts":
        if user_id != ADMIN_ID: return
        accs = "\n".join([f"• `{a['user_id']}`" for a in saved_accounts]) or "None"
        await callback_query.message.reply_text(f"📂 **Accounts:**\n{accs}")
    elif data == "admin_view_channels":
        if user_id != ADMIN_ID: return
        chns = "\n".join([f"• `{c['channel']}`" for c in saved_channels]) or "None"
        await callback_query.message.reply_text(f"📢 **Channels:**\n{chns}")
    elif data == "start_campaign":
        await callback_query.message.reply_text("🚀 Mass DM Campaign menu opened!")
    elif data == "set_message":
        await callback_query.message.reply_text("✍️ Send the message you want to set.")
    elif data == "preview_message":
        await callback_query.message.reply_text("👀 Message preview...")
    elif data == "my_account":
        ac = len([a for a in saved_accounts if a['user_id'] == user_id])
        cc = len([c for c in saved_channels if c['user_id'] == user_id])
        await callback_query.message.reply_text(f"👤 **Account Info:**\nAccounts: {ac}\nChannels: {cc}")
    elif data == "vip_premium":
        await callback_query.message.reply_text("⭐ VIP Premium feature.")
    elif data == "redeem_code":
        await callback_query.message.reply_text("🎁 Enter redeem code:")
    elif data == "add_account":
        user_states[user_id] = "waiting_for_session"
        await callback_query.message.reply_text("➕ Send your Pyrogram **Session String**:")
    elif data == "remove_account":
        await callback_query.message.reply_text("❌ Send account to remove.")
    elif data == "add_channel":
        user_states[user_id] = "waiting_for_channel"
        await callback_query.message.reply_text("➕ Send Channel Username/Link:")
    elif data == "join_request_dm":
        user_states[user_id] = "waiting_for_join_channel"
        await callback_query.message.reply_text("🤝 Send Channel Username/Link for Join DM:")
    elif data == "how_to_use":
        await callback_query.message.reply_text("❓ Guide on how to use.")
    elif data == "support":
        await callback_query.message.reply_text("🛠️ Support contact.")

@app.on_message(filters.text & ~filters.command(["start", "admin"]))
async def handle_text_messages(client, message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = user_states.get(user_id)
    bot_users.add(user_id)
    
    if state == "waiting_for_broadcast" and user_id == ADMIN_ID:
        user_states.pop(user_id, None)
        await message.reply_text("⏳ Broadcasting...")
        for u_id in list(bot_users):
            try: await client.send_message(u_id, f"📢 **Broadcast:**\n{text}")
            except: pass
        await message.reply_text("✅ Broadcast completed!")
    elif state == "waiting_for_session":
        if len(text) < 50:
            await message.reply_text("⚠️ Invalid Session String!")
            return
        saved_accounts.append({"user_id": user_id, "session": text})
        user_states.pop(user_id, None)
        await message.reply_text("✅ Account Saved!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))
    elif state == "waiting_for_channel":
        saved_channels.append({"user_id": user_id, "channel": text})
        user_states.pop(user_id, None)
        await message.reply_text(f"✅ Channel Saved: `{text}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))
    elif state == "waiting_for_join_channel":
        temp_join_data[user_id] = {"channel": text}
        user_states[user_id] = "waiting_for_join_message"
        await message.reply_text("✅ Channel saved. Now send the DM message:")
    elif state == "waiting_for_join_message":
        channel = temp_join_data.get(user_id, {}).get("channel")
        active_join_configs[channel] = text
        user_states.pop(user_id, None)
        temp_join_data.pop(user_id, None)
        await message.reply_text("✅ Join Request DM configured successfully!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))

@app.on_chat_join_request()
async def auto_join_request_handler(client, join_request):
    chat = join_request.chat
    user = join_request.from_user
    key = f"@{chat.username}" if chat.username else str(chat.id)
    if key in active_join_configs:
        try: await client.send_message(user.id, active_join_configs[key])
        except Exception as e: print(e)

if __name__ == "__main__":
    # Flask server ko background thread mein start kar diya hai
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Bot is starting cleanly without errors...")
    app.run()
