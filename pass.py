import time
import requests
from curl_cffi import requests as curl_requests

# ================= НАЛАШТУВАННЯ =================
TELEGRAM_TOKEN = "8797587395:AAGGdVxbNL-R3kAJNie24y3t09uvNJXCYXc"

# Список Chat ID (ваш, батька, брата та мами)
CHAT_IDS = [
    "5108112045",  # Ваш ID
    "5089008489",  # ID батька
    "840192155",   # ID брата
    "530596411",   # ID брата Аріка
    "6409909256",   # ID баті Аріка
    "935551950"    # ID мами
]

# Польський ротаційний проксі
PROXY_URL = "http://f4cf95bdfb4aa722f51d__cr.pl;state.mazovia;anon.1:e6f8adf0b61673a1@46.4.139.124:823"

# Список сайтів для моніторингу
SITES = [
    {
        "name": "Кортрейк (Бельгія)",
        "url": "https://kortrijk.pasport.org.ua/solutions/e-queue"
    },
    {
        "name": "Кельн (Німеччина)",
        "url": "https://cologne.pasport.org.ua/solutions/e-queue"
    }
]

CHECK_INTERVAL = 60  # Інтервал між перевірками (в секундах)

def send_telegram(message):
    """Надсилання сповіщення усім користувачам"""
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    for chat_id in CHAT_IDS:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            if not response.json().get("ok"):
                print(f"Помилка відправки для ID {chat_id}: {response.json()}")
        except Exception as e:
            print(f"Помилка з'єднання з Telegram API для ID {chat_id}: {e}")

def main():
    target_phrase = "Наразі всі місця зайняті"
    
    proxies = None
    if PROXY_URL:
        proxies = {"http": PROXY_URL, "https": PROXY_URL}

    print("Запуск моніторингу Кортрейка та Кельна...")
    send_telegram(
        "🤖 <b>Бот моніторингу оновлено!</b>\n"
        "Повернуто відстеження двох локацій:\n"
        "• Кортрейк (Бельгія)\n"
        "• Кельн (Німеччина)"
    )

    while True:
        # Нова сесія створюється на кожному колі для зміни IP
        session = curl_requests.Session(impersonate="chrome120", proxies=proxies)
        
        for site in SITES:
            city_name = site["name"]
            site_url = site["url"]
            
            try:
                response = session.get(site_url, timeout=20)
                
                if response.status_code == 200:
                    if target_phrase not in response.text:
                        alert_text = (
                            f"🚨 <b>УВАГА! З'ЯВИЛИСЯ ВІЛЬНІ МІСЦЯ!</b> 🚨\n\n"
                            f"📍 <b>Локація:</b> {city_name}\n"
                            f"Напис <i>'{target_phrase}'</i> зник із сайту!\n\n"
                            f"🔗 <b>Мерщій переходьте за посиланням:</b>\n{site_url}"
                        )
                        print(f"[{time.strftime('%H:%M:%S')}] МІСЦЯ З'ЯВИЛИСЯ у {city_name}! Надсилаю сповіщення...")
                        
                        for _ in range(3):
                            send_telegram(alert_text)
                            time.sleep(2)
                            
                        time.sleep(600)
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] {city_name}: Місць немає (Код 200 ОК).")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] {city_name}: Помилка HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] {city_name}: Збій при запиті — {e}")
                
            time.sleep(10)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
