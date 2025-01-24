import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from ad_accounts import AD_ACCOUNTS

def send_telegram_notification(messages):
    if messages:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"🚨 На текущий момент - {current_time}, израсходован бюджет:\n\n"
        message = header + "\n".join(messages)
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, data=data)
        print(f"Статус отправки: {response.status_code}, Ответ: {response.text}")
    else:
        print("Нет ошибок оплаты, уведомления не отправляются.")

load_dotenv()

FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Ошибка: TELEGRAM_BOT_TOKEN не загружен. Проверьте файл .env")
if not TELEGRAM_CHAT_ID:
    raise ValueError("Ошибка: TELEGRAM_CHAT_ID не загружен. Проверьте файл .env")

def get_ad_account_status(account_id):
    url = f"https://graph.facebook.com/v18.0/{account_id}"
    params = {
        "fields": "account_id,name,account_status,balance",
        "access_token": FACEBOOK_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Ошибка: Таймаут при запросе к API Facebook для {account_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
    return None

def check_ad_accounts():
    messages = []
    for account_id, account_info in AD_ACCOUNTS.items():
        account_data = get_ad_account_status(account_id)
        if account_data:
            status = account_data.get("account_status")
            balance = int(account_data.get("balance", 0)) / 100
            if status == 3:
                message = f"🔴 {account_info['ad_name']} | ошибка оплаты ➡️ ${balance} - {account_info['name']}"
                messages.append(message)
        else:
            print(f"Ошибка при проверке {account_id}")
    send_telegram_notification(messages)


if __name__ == "__main__":
    check_ad_accounts()
