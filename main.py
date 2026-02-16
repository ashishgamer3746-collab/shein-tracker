import telebot
import time
import requests
import cloudscraper
from threading import Thread
from flask import Flask
import os

# --- AAPKA DATA ---
API_TOKEN = '7774900746:AAHVVv9Y-p3z3hVOfX81C_lE067H70pM0OQ' 
ADMIN_ID = '7259654109' 
# Ye wo main page hai jahan flash sale aati hai
SCAN_TARGETS = [
    "https://m.shein.com/in/SHEIN-Verse-vc-75677.html",
    "https://m.shein.com/in/flash-sale-sc-00500122.html" 
]

bot = telebot.TeleBot(API_TOKEN)
scraper = cloudscraper.create_scraper()
app = Flask(__name__)

@app.route('/')
def home():
    return "Auto-Scanner is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def auto_scanner():
    already_sent = set() # Taaki ek hi link bar-bar na aaye
    while True:
        for target_url in SCAN_TARGETS:
            try:
                response = scraper.get(target_url, timeout=15)
                # Ye logic page ke andar se naye "In Stock" links dhoondega
                if "in stock" in response.text.lower() or "add to cart" in response.text.lower():
                    if target_url not in already_sent:
                        bot.send_message(ADMIN_ID, f"🔥 **AUTO-DETECTED STOCK!**\n\nLink: {target_url}\nStatus: CURRENTLY IN STOCK!")
                        already_sent.add(target_url)
            except Exception as e:
                print(f"Error scanning: {e}")
        
        time.sleep(30) # Har 30 second mein check karega

if __name__ == "__main__":
    Thread(target=run_flask).start()
    Thread(target=auto_scanner).start()
    bot.polling(none_stop=True)
