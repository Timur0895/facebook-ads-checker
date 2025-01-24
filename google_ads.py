import requests
from google.ads.google_ads.client import GoogleAdsClient
from dotenv import load_dotenv
import os

load_dotenv()

# Загрузка конфигурации из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

# Подключение к Google Ads API
client = GoogleAdsClient.load_from_storage("google_ads.yaml")

def get_google_ads_balance():
    query = """
        SELECT customer.descriptive_name, customer.currency_code, customer.payments_account_info.payments_account_name
        FROM customer
    """
    response = client.service.google_ads.search(customer_id=GOOGLE_CUSTOMER_ID, query=query)
    for row in response:
        return f"Аккаунт: {row.customer.descriptive_name}, Валюта: {row.customer.currency_code}, Платежный аккаунт: {row.customer.payments_account_info.payments_account_name}"

def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    print("Статус отправки:", response.status_code)

if __name__ == "__main__":
    balance_info = get_google_ads_balance()
    send_telegram_notification(balance_info)
