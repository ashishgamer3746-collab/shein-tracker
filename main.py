import telebot
import time
import cloudscraper
from threading import Thread

# --- CONFIGURATION ---
API_TOKEN = '7728175589:AAFJa9M6lyyeoLzx93r46CxrWN0LksMkkto'
ADMIN_ID = 7259654109 

bot = telebot.TeleBot(API_TOKEN)
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'android', 'desktop': False})

is_scanning = True
total_scans = 0

@bot.message_handler(commands=['start', 'stats'])
def handle_commands(message):
    if message.from_user.id == ADMIN_ID:
        status = "✅ Active" if is_scanning else "❌ Offline"
        msg = (f"👑 *SHEIN TRACKER PRO*\n\n"
               f"📊 Status: {status}\n"
               f"🔍 Total Scans: {total_scans}\n"
               f"Bot scan kar raha hai...")
        bot.reply_to(message, msg, parse_mode='Markdown')

def scanner_loop():
    global total_scans
    url = "https://m.shein.in/in/SHEIN-Verse-vc-75677.html"
    while is_scanning:
        try:
            total_scans += 1
            response = scraper.get(url, timeout=30)
            if "in stock" in response.text.lower() or "add to cart" in response.text.lower():
                bot.send_message(ADMIN_ID, f"🚨 *STOCK ALERT!* 🚨\n\nLink: {url}")
        except Exception as e:
            print(f"Scan Error (VPN check karo): {e}")
        time.sleep(60)

if __name__ == "__main__":
    # 1. Scanner start karo
    Thread(target=scanner_loop, daemon=True).start()
    print("🚀 Scanner Started...")
    
    # 2. Telegram message sunna start karo (Ye fix hai)
    while True:
        try:
            print("🤖 Bot is listening for commands...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Polling Error: {e}")
            time.sleep(5)
