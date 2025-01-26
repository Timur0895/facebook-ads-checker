import asyncio
import os
import subprocess
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Флаг для остановки проверки
checking_process = {}

# Клавиатура с кнопками
keyboard = [
    ["✅ Проверка"],
    ["🛑 Остановить проверку"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# Приветственное сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    checking_process[update.effective_chat.id] = False
    await update.message.reply_text(
        "Нажми ✅ для проверки.",
        reply_markup=reply_markup
    )

# Логика процесса проверки (запуск main.py)
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    checking_process[chat_id] = True

    await update.message.reply_text("🔍 Идёт проверка... Пожалуйста, подождите.")

    try:
        # Запуск файла main.py и получение результата
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)

        if checking_process[chat_id]:  # Если проверка не остановлена
            await update.message.reply_text("✅ Проверка завершена.")
        else:
            await update.message.reply_text("🛑 Проверка остановлена.")
    
    except Exception as e:
        await update.message.reply_text(f"⚠ Произошла ошибка: {str(e)}")
    
    await start(update, context)

# Остановка проверки
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    checking_process[chat_id] = False
    await update.message.reply_text("🛑 Проверка остановлена.")
    await start(update, context)

# Запуск бота
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("✅ Проверка"), check))
    app.add_handler(MessageHandler(filters.Regex("🛑 Остановить проверку"), stop))

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
