from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import os
import threading

# Render ke liye chota web server
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running live with Admin Panel!"

# ==================== CONFIGURATION ====================
API_ID = 36645562  # Apna numeric api_id daalein
API_HASH = "ccad405579d80b82492abbf4a7777907"
BOT_TOKEN = "8822648253:AAGZroIwI4F7udtFlhABotrsqjAXm_qcSq4"
ADMIN_ID = 8895089247  # ⚠️ Yahan APNA Telegram User ID daalein (Bina quotes ke)
# =======================================================

app = Client(
    "dms_forward_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Global Storage Variables
user_states = {}
temp_join_data = {}
bot_users = set()       # Un sabhi users ke IDs jinhone /start dabaya hai
saved_accounts = []     # Added accounts list
saved_channels = []     # Added channels list
active_join_configs = {} # Channel -> DM Message mapping


# Main User Keyboard Menu
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
    
    # Agar user ADMIN hai, toh Admin Panel ka button bhi add kar do
    if user_id == ADMIN_ID:
        buttons.insert(0, [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")])
        
    return InlineKeyboardMarkup(buttons)


# Admin Special Keyboard Menu
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
    bot_users.add(user_id)  # Track user for broadcast
    user_states.pop(user_id, None)
    
    text = (
        "**🤖 DMS FORWARD BOT MENU**\n\n"
        "Welcome! Please choose an option below:"
    )
    await message.reply_text(text, reply_markup=get_main_menu(user_id))


# Direct /admin Command Handler
@app.on_message(filters.command("admin") & filters.user(ADMIN_ID))
async def admin_command_handler(client, message):
    await message.reply_text(
        "**👑 WELCOME TO ADMIN PANEL**\n\n"
        "Control and monitor all bot features from here:",
        reply_markup=get_admin_menu()
    )


@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    await callback_query.answer()
    
    # Main Navigation
    if data == "main_menu":
        user_states.pop(user_id, None)
        await callback_query.message.edit_text(
            "**🤖 DMS FORWARD BOT MENU**\n\nWelcome back!",
            reply_markup=get_main_menu(user_id)
        )
        
    # ==================== ADMIN PANEL CALLBACKS ====================
    elif data == "admin_panel":
        if user_id != ADMIN_ID:
            await callback_query.message.reply_text("❌ You are not authorized to access Admin Panel.")
            return
        await callback_query.message.edit_text(
            "**👑 WELCOME TO ADMIN PANEL**\n\n"
            "Select an action below:",
            reply_markup=get_admin_menu()
        )
        
    elif data == "admin_stats":
        if user_id != ADMIN_ID: return
        stats_text = (
            "**📊 SYSTEM BOT STATS:**\n\n"
            f"👤 **Total Users:** {len(bot_users)}\n"
            f"🔑 **Total Linked Accounts (Sessions):** {len(saved_accounts)}\n"
            f"📢 **Total Linked Channels:** {len(saved_channels)}\n"
            f"🤝 **Active Join DM Configs:** {len(active_join_configs)}"
        )
        await callback_query.message.edit_text(stats_text, reply_markup=get_admin_menu())

    elif data == "admin_broadcast":
        if user_id != ADMIN_ID: return
        user_states[user_id] = "waiting_for_broadcast"
        await callback_query.message.reply_text(
            "📢 **Broadcast System:**\n\n"
            "Abhi woh Message type karke bhejo jo aapko **SABHI BOT USERS** ko bhejnah hai:\n"
            "*(Type /start to cancel)*"
        )

    elif data == "admin_view_accounts":
        if user_id != ADMIN_ID: return
        if not saved_accounts:
            await callback_query.message.reply_text("📂 No accounts added yet.")
            return
        acc_info = "\n".join([f"• User ID: `{acc['user_id']}`" for acc in saved_accounts])
        await callback_query.message.reply_text(f"📂 **All Saved Accounts:**\n\n{acc_info}")

    elif data == "admin_view_channels":
        if user_id != ADMIN_ID: return
        if not saved_channels:
            await callback_query.message.reply_text("📢 No channels added yet.")
            return
        chn_info = "\n".join([f"• `{chn['channel']}` (User: `{chn['user_id']}`)" for chn in saved_channels])
        await callback_query.message.reply_text(f"📢 **All Saved Channels:**\n\n{chn_info}")

    # ==================== USER MENU CALLBACKS ====================
    elif data == "start_campaign":
        await callback_query.message.reply_text("🚀 Mass DM Campaign menu opened!")
    elif data == "set_message":
        await callback_query.message.reply_text("✍️ Send the message you want to set for campaigns.")
    elif data == "preview_message":
        await callback_query.message.reply_text("👀 Here is your message preview...")
    elif data == "my_account":
        acc_count = len([acc for acc in saved_accounts if acc['user_id'] == user_id])
        chn_count = len([chn for chn in saved_channels if chn['user_id'] == user_id])
        await callback_query.message.reply_text(
            f"👤 **Your Account Info:**\n"
            f"Linked Accounts: {acc_count}\n"
            f"Linked Channels: {chn_count}"
        )
    elif data == "vip_premium":
        await callback_query.message.reply_text("⭐ Upgrade to VIP Premium for unlimited sends.")
    elif data == "redeem_code":
        await callback_query.message.reply_text("🎁 Enter your redeem code:")
    elif data == "add_account":
        user_states[user_id] = "waiting_for_session"
        await callback_query.message.reply_text(
            "➕ **Add Account:**\n\n"
            "Please send your Pyrogram **Session String** now.\n"
            "*(Type /start to cancel)*"
        )
    elif data == "remove_account":
        await callback_query.message.reply_text("❌ Send the account number or session to remove.")
    elif data == "add_channel":
        user_states[user_id] = "waiting_for_channel"
        await callback_query.message.reply_text(
            "➕ **Add Channel:**\n\n"
            "Please send your **Channel Username or Link** (jaise `@mychannel`):\n"
            "*(Type /start to cancel)*"
        )
    elif data == "join_request_dm":
        user_states[user_id] = "waiting_for_join_channel"
        await callback_query.message.reply_text(
            "🤝 **Join Request DM Setup:**\n\n"
            "Pehle apne **Channel ka Username ya Link** bhejo (jaise `@mychannel`):\n"
            "*(Dhyan rahe bot us channel me Admin hona chahiye)*"
        )
    elif data == "how_to_use":
        await callback_query.message.reply_text("❓ Guide: How to use this bot.")
    elif data == "support":
        await callback_query.message.reply_text("🛠️ Contact support here.")


# Text Messages Handler (For Broadcast, Sessions, Channels, Join Request)
@app.on_message(filters.text & ~filters.command(["start", "admin"]))
async def handle_text_messages(client, message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = user_states.get(user_id)
    bot_users.add(user_id)
    
    # 1. Admin Broadcast State
    if state == "waiting_for_broadcast" and user_id == ADMIN_ID:
        user_states.pop(user_id, None)
        sent = 0
        failed = 0
        await message.reply_text("⏳ Broadcast in progress...")
        
        for u_id in list(bot_users):
            try:
                await client.send_message(u_id, f"📢 **ADMIN BROADCAST:**\n\n{text}")
                sent += 1
            except Exception:
                failed += 1
                
        await message.reply_text(f"✅ **Broadcast Completed!**\n\nSuccessful: {sent}\nFailed: {failed}")

    # 2. Add Account State
    elif state == "waiting_for_session":
        if len(text) < 50:
            await message.reply_text("⚠️ Invalid Session String! Please send a valid string or type /start to cancel.")
            return
        
        saved_accounts.append({"user_id": user_id, "session": text})
        user_states.pop(user_id, None)
        await message.reply_text("✅ **Account Successfully Added & Saved!** 🎉", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))
    
    # 3. Add Channel State
    elif state == "waiting_for_channel":
        saved_channels.append({"user_id": user_id, "channel": text})
        user_states.pop(user_id, None)
        await message.reply_text(
            f"✅ **Channel Successfully Added!** 🎉\n\nChannel: `{text}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))

    # 4. Join Request Step 1
    elif state == "waiting_for_join_channel":
        temp_join_data[user_id] = {"channel": text}
        user_states[user_id] = "waiting_for_join_message"
        await message.reply_text(
            f"✅ Channel saved: `{text}`\n\n"
            "Ab woh **Message** bhejo jo aapko user ko Join Request accept hone par ya DM mein bhejna hai:"
        )
    
    # 5. Join Request Step 2
    elif state == "waiting_for_join_message":
        channel = temp_join_data.get(user_id, {}).get("channel")
        active_join_configs[channel] = text
        user_states.pop(user_id, None)
        temp_join_data.pop(user_id, None)
        
        await message.reply_text(
            f"✅ **Join Request DM Configured Successfully!** 🎉\n\n"
            f"Channel: `{channel}`\nMessage set ho gaya hai.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))


# Automatic Join Request Listener
@app.on_chat_join_request()
async def auto_join_request_handler(client, join_request):
    chat = join_request.chat
    user = join_request.from_user
    channel_key = f"@{chat.username}" if chat.username else str(chat.id)
    
    if channel_key in active_join_configs:
        msg_to_send = active_join_configs[channel_key]
        try:
            await client.send_message(user.id, msg_to_send)
        except Exception as e:
            print(f"Failed to send join request DM: {e}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: web_app.run(host="0.0.0.0", port=port)).start()
    
    print("Bot with Admin Panel is starting...")
    app.run()
