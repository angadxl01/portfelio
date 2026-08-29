import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import os
import threading
import json

# ==================== CONFIGURATION ====================
API_ID = 36645562
API_HASH = "ccad405579d80b82492abbf4a7777907"
BOT_TOKEN = "8822648253:AAGZroIwI4F7udtFlhABotrsqjAXm_qcSq4"
ADMIN_ID = 8895089247
# =======================================================

# Flask server to satisfy Render's port binding requirement
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

app = Client(
    "dms_forward_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user_states = {}
temp_login_data = {}
bot_users = set()
saved_channels = []
active_join_configs = {}
user_messages = {}  # 👈 Users ke custom messages store karne ke liye dictionary

ACCOUNTS_FILE = "saved_accounts.json"

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_accounts_data(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

saved_accounts = load_accounts()

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
            InlineKeyboardButton("➕ Add Account (Login)", callback_data="add_account")
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

@app.on_message(filters.command("admin"))
async def admin_command_handler(client, message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.reply_text("❌ You are not authorized to use the admin panel!")
        return
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
        accs = "\n".join([f"• User ID: `{a['user_id']}`" for a in saved_accounts]) or "None"
        await callback_query.message.reply_text(f"📂 **Saved Accounts:**\n{accs}")
    elif data == "admin_view_channels":
        if user_id != ADMIN_ID: return
        chns = "\n".join([f"• `{c['channel']}`" for c in saved_channels]) or "None"
        await callback_query.message.reply_text(f"📢 **Channels:**\n{chns}")
    elif data == "start_campaign":
        await callback_query.message.reply_text("🚀 Mass DM Campaign menu opened!")
    elif data == "set_message":
        # 👈 Set Message Logic
        user_states[user_id] = "waiting_for_message"
        await callback_query.message.reply_text(
            "✍️ **Set Campaign Message**\n\nPlease send the text message you want to send in your Mass DM campaign:"
        )
    elif data == "preview_message":
        # 👈 Preview Message Logic
        msg = user_messages.get(user_id, "⚠️ No message set yet! Please use 'Set Message' first.")
        await callback_query.message.reply_text(
            f"👀 **Your Message Preview:**\n\n{msg}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
        )
    elif data == "my_account":
        ac = len([a for a in saved_accounts if a['user_id'] == user_id])
        cc = len([c for c in saved_channels if c['user_id'] == user_id])
        await callback_query.message.reply_text(f"👤 **Your Account Info:**\nLogged-in Accounts: {ac}\nChannels: {cc}")
    elif data == "vip_premium":
        await callback_query.message.reply_text("⭐ VIP Premium feature.")
    elif data == "redeem_code":
        await callback_query.message.reply_text("🎁 Enter redeem code:")
    elif data == "add_account":
        user_states[user_id] = "waiting_for_phone"
        temp_login_data[user_id] = {}
        await callback_query.message.reply_text(
            "📱 **Phone Number Login**\n\nPlease send your phone number with country code (e.g., `+919876543210`):"
        )
    elif data == "remove_account":
        await callback_query.message.reply_text("❌ Send account details to remove.")
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
        
    elif state == "waiting_for_message":
        # 👈 Saving the custom message
        user_messages[user_id] = text
        user_states.pop(user_id, None)
        await message.reply_text(
            "✅ **Message Saved Successfully!**\nYou can check it anytime using 'Preview Message'.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
        )

    elif state == "waiting_for_phone":
        phone_number = text
        temp_login_data[user_id]["phone"] = phone_number
        
        status_msg = await message.reply_text("⏳ Connecting to Telegram and sending OTP...")
        try:
            temp_client = Client(f"temp_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
            await temp_client.connect()
            sent_code = await temp_client.send_code(phone_number)
            
            temp_login_data[user_id]["client"] = temp_client
            temp_login_data[user_id]["phone_code_hash"] = sent_code.phone_code_hash
            
            user_states[user_id] = "waiting_for_otp"
            await status_msg.edit_text("✅ OTP sent to your Telegram app!\n\nPlease send the OTP code with spaces (e.g., `1 2 3 4 5`):")
        except Exception as e:
            await status_msg.edit_text(f"❌ Error: `{str(e)}`\n\nTry again by clicking 'Add Account' from menu.")
            user_states.pop(user_id, None)
            temp_login_data.pop(user_id, None)
            
    elif state == "waiting_for_otp":
        otp_code = text.replace(" ", "")
        login_data = temp_login_data.get(user_id, {})
        temp_client = login_data.get("client")
        phone = login_data.get("phone")
        phone_code_hash = login_data.get("phone_code_hash")
        
        status_msg = await message.reply_text("⏳ Verifying OTP...")
        try:
            await temp_client.sign_in(phone, phone_code_hash, otp_code)
            session_string = await temp_client.export_session_string()
            await temp_client.disconnect()
            
            saved_accounts.append({"user_id": user_id, "session": session_string})
            save_accounts_data(saved_accounts)
            
            user_states.pop(user_id, None)
            temp_login_data.pop(user_id, None)
            await status_msg.edit_text(
                "✅ **Account Login Successful!**\nYour session has been securely saved.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
            )
        except Exception as e:
            if "SESSION_PASSWORD_NEEDED" in str(e) or "Password" in str(e):
                user_states[user_id] = "waiting_for_2fa"
                await status_msg.edit_text("🔐 Two-Step Verification (2FA) is enabled.\n\nPlease send your account password:")
            else:
                await status_msg.edit_text(f"❌ Login Failed: `{str(e)}`")
                try: await temp_client.disconnect()
                except: pass
                user_states.pop(user_id, None)
                temp_login_data.pop(user_id, None)
                
    elif state == "waiting_for_2fa":
        password = text
        login_data = temp_login_data.get(user_id, {})
        temp_client = login_data.get("client")
        
        status_msg = await message.reply_text("⏳ Verifying Password...")
        try:
            await temp_client.check_password(password)
            session_string = await temp_client.export_session_string()
            await temp_client.disconnect()
            
            saved_accounts.append({"user_id": user_id, "session": session_string})
            save_accounts_data(saved_accounts)
            
            user_states.pop(user_id, None)
            temp_login_data.pop(user_id, None)
            await status_msg.edit_text(
                "✅ **Account Login Successful with 2FA!**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
            )
        except Exception as e:
            await status_msg.edit_text(f"❌ Invalid Password: `{str(e)}`")
            try: await temp_client.disconnect()
            except: pass
            user_states.pop(user_id, None)
            temp_login_data.pop(user_id, None)

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

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await app.start()
    print("Bot is running with Set Message & Preview features!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
