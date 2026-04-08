import os
import aiohttp
import asyncio
from urllib.parse import urlparse
from pyrogram import Client, filters

# Environment Variables ကနေ အချက်အလက်တွေ ယူပါမယ်
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("video_uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# "http" သို့မဟုတ် "https" နဲ့ စတဲ့ လင့်ခ်တွေကို လက်ခံပါမယ်
@app.on_message(filters.regex(r'^https?://'))
async def process_link(client, message):
    url = message.text.strip()
    status_msg = await message.reply_text("📥 စတင် ဒေါင်းလုဒ်ဆွဲနေပါပြီ... (ကျေးဇူးပြု၍ ခဏစောင့်ပါ)")
    
    # URL ကနေ ဖိုင်နာမည် ခွဲထုတ်ခြင်း
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename.endswith('.mp4'):
        filename = "downloaded_video.mp4"
        
    try:
        # Aiohttp အသုံးပြုပြီး အမြန်ဆုံးနှင့် အငြိမ်ဆုံး ဒေါင်းလုဒ်ဆွဲခြင်း
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                with open(filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
        
        await status_msg.edit_text("📤 Telegram သို့ Streamable အဖြစ် ပြန်လည် Upload လုပ်နေပါပြီ...")
        
        # Telegram သို့ Upload လုပ်ခြင်း
        await client.send_video(
            chat_id=message.chat.id,
            video=filename,
            supports_streaming=True, # Streamable ဖြစ်စေရန် အရေးကြီးဆုံးအပိုင်း
            caption="✅ Upload Completed Successfully!"
        )
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error ဖြစ်သွားပါသည်: {e}")
        
    finally:
        # Server ပေါ်တွင် နေရာမစားအောင် ဒေါင်းလုဒ်ဆွဲထားသောဖိုင်ကို ချက်ချင်းပြန်ဖျက်ခြင်း
        if os.path.exists(filename):
            os.remove(filename)

print("Bot is successfully running...")
app.run()
