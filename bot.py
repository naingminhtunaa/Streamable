import os
import aiohttp
import asyncio
from aiohttp import web
from urllib.parse import urlparse
from pyrogram import Client, filters
from pyrogram import idle

# --- အချက်အလက်များ ရယူခြင်း ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEB_URL = os.environ.get("WEB_URL", "https://your-app.koyeb.app") # နောက်မှ Koyeb လင့်ခ်ပြောင်းထည့်ရန်

# Bot ကို တည်ဆောက်ခြင်း
app = Client("my_stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Web Server အတွက် လမ်းကြောင်းများ (Routes)
routes = web.RouteTableDef()

# အခြေခံ Web Page (Server အလုပ်လုပ်မလုပ် စစ်ရန်)
@routes.get('/')
async def hello(request):
    return web.Response(text="✅ Stream Bot Web Server is Running perfectly!")

# Stream ကြည့်ရန် လမ်းကြောင်း (ဒီကနေ Video ကို တိုက်ရိုက်ပြပေးပါမယ်)
@routes.get('/watch/{filename}')
async def watch_video(request):
    filename = request.match_info['filename']
    if os.path.exists(filename):
        # FileResponse က Stream ဆွဲတာ၊ အရှေ့ကျော်တာ (Forward) တွေကို အလိုအလျောက် Support ပေးပါတယ်
        return web.FileResponse(filename)
    return web.Response(text="❌ ဤဖိုင်ကို ရှာမတွေ့ပါ။", status=404)

# --- Bot ၏ လုပ်ဆောင်ချက်များ ---
@app.on_message(filters.regex(r'^https?://'))
async def process_link(client, message):
    url = message.text.strip()
    status_msg = await message.reply_text("📥 Koyeb Server ပေါ်သို့ ဆွဲတင်နေပါပြီ... (ခဏစောင့်ပါ)")
    
    # URL ကနေ ဖိုင်နာမည် ခွဲထုတ်ခြင်း (နာမည်ရှည်ရင် error တက်နိုင်လို့ အသေပေးလိုက်ပါတယ်)
    import time
    filename = f"video_{int(time.time())}.mp4" 
        
    try:
        # Aiohttp ဖြင့် Server ပေါ် ဒေါင်းလုဒ်ဆွဲခြင်း
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                with open(filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
        
        # Web Link အသစ် ဖန်တီးခြင်း
        stream_link = f"{WEB_URL}/watch/{filename}"
        
        text = (
            "✅ **လုပ်ဆောင်မှု အောင်မြင်ပါသည်။**\n\n"
            "🎬 **Streamable Video Link:**\n"
            f"👉 `{stream_link}`\n\n"
            "*(အထက်ပါ လင့်ခ်ကို Browser, MX Player သို့မဟုတ် VLC တွင် ထည့်သွင်းကြည့်ရှုနိုင်ပါသည်။)*"
        )
        await status_msg.edit_text(text)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error ဖြစ်သွားပါသည်: {e}")

# --- Web Server ကို အသက်သွင်းမည့် Function ---
async def start_web_server():
    webapp = web.Application()
    webapp.add_routes(routes)
    runner = web.AppRunner(webapp)
    await runner.setup()
    
    # Koyeb က ပုံမှန်အားဖြင့် Port 8000 ကို သုံးပါတယ်
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server started on port {port}")

# --- Bot နှင့် Web Server နှစ်ခုစလုံးကို တစ်ပြိုင်နက် Run မည့် အဓိက Function ---
async def main():
    print("🤖 Starting Bot...")
    await app.start()
    
    print("🌐 Starting Web Server...")
    await start_web_server()
    
    print("✅ Everything is running successfully!")
    await idle() # Bot ကို အမြဲ Run နေအောင် ထားခြင်း
    await app.stop()

# Program စတင်ခြင်း
if __name__ == '__main__':
    app.run(main())
