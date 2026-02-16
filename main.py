import telebot
import cloudscraper
import time
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Lock

# ================= CONFIGURATION =================
API_TOKEN = '7728175589:AAGm8a5e7Ir98DZ5XXfxFX8RFK-d7ssAz5k'
ADMIN_ID = 8334184096

VERSE_URL = "https://www.shein.com/trends/SHEIN-Verse-vc-75677.html"
CLOTH_SIZES = ['XS', 'S', 'M', 'L']
SCAN_INTERVAL = 60 
MAX_WORKERS = 100

bot = telebot.TeleBot(API_TOKEN)
scraper = cloudscraper.create_scraper()
verse_products = {} 
lock = Lock()

# ================= MONITORING ENGINE =================

def discover_products():
    print("🔍 Scanning Shein Verse...")
    try:
        res = scraper.get(VERSE_URL, timeout=20)
        if res.status_code == 200:
            links = re.findall(r'href="(/.*?\.html)"', res.text)
            with lock:
                for link in set(links):
                    full_url = "https://www.shein.com" + link
                    if full_url not in verse_products:
                        verse_products[full_url] = []
    except Exception as e:
        print(f"Discovery Error: {e}")

def scan_item(url):
    try:
        res = scraper.get(url, timeout=10)
        if res.status_code != 200: return
        html = res.text.upper()
        
        name_match = re.search(r'<TITLE>(.*?)</TITLE>', html)
        name = name_match.group(1).split('|')[0].strip() if name_match else "Shein Item"
        
        current_stock = []
        for s in CLOTH_SIZES:
            if f'"{s}"' in html and "ADD TO BAG" in html:
                current_stock.append(s)
        
        if ("SIZE 0" in html or "ONE-SIZE" in html) and "ADD TO BAG" in html:
            current_stock.append("Size 0 (Ornament)")

        with lock:
            last_stock = verse_products.get(url, [])
            new_arrivals = [s for s in current_stock if s not in last_stock]
            if new_arrivals:
                msg = (f"🚀 **SHEIN ALERT!**\n\n"
                       f"📦 **Item:** {name}\n"
                       f"✅ **Stock In:** {', '.join(new_arrivals)}\n\n"
                       f"🔗 [VIEW PRODUCT]({url})")
                bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")
            verse_products[url] = current_stock
    except:
        pass

def monitor_engine():
    global SCAN_INTERVAL
    while True:
        discover_products()
        all_urls = list(verse_products.keys())
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(scan_item, all_urls)
        time.sleep(SCAN_INTERVAL)

# ================= ADMIN PANEL COMMANDS =================

@bot.message_handler(commands=['start'])
def start_msg(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "👑 **Admin Panel Active!**\n\nCommands:\n/stats - Check bot status\n/add_link <url> - Add manual link\n/speed <sec> - Change scan delay")
    else:
        bot.reply_to(message, "❌ Access Denied.")

@bot.message_handler(commands=['stats'])
def get_stats(message):
    if message.from_user.id == ADMIN_ID:
        count = len(verse_products)
        bot.reply_to(message, f"📊 **Bot Stats:**\n\nTotal Links being scanned: {count}\nSpeed: Every {SCAN_INTERVAL} seconds\nWorkers: {MAX_WORKERS}")

@bot.message_handler(commands=['add_link'])
def add_manual(message):
    if message.from_user.id == ADMIN_ID:
        try:
            url = message.text.split()[1]
            if "shein.com" in url:
                with lock:
                    verse_products[url] = []
                bot.reply_to(message, "✅ Link added to scanner!")
            else:
                bot.reply_to(message, "❌ Invalid Shein URL.")
        except:
            bot.reply_to(message, "📝 Use: /add_link <url>")

@bot.message_handler(commands=['speed'])
def change_speed(message):
    global SCAN_INTERVAL
    if message.from_user.id == ADMIN_ID:
        try:
            new_speed = int(message.text.split()[1])
            SCAN_INTERVAL = new_speed
            bot.reply_to(message, f"⚡ Speed changed to {new_speed} seconds.")
        except:
            bot.reply_to(message, "📝 Use: /speed <seconds>")

if __name__ == "__main__":
    Thread(target=monitor_engine, daemon=True).start()
    print("🔥 Bot Online with Admin Panel...")
    bot.infinity_polling()
