import os
import telebot
import sqlite3
import re
from flask import Flask, request

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8605589109:AAGhfC7fzRi7pFPxwGXtJbgWitZSDOezz94")
RAILWAY_STATIC_URL = os.environ.get("RAILWAY_STATIC_URL")

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

def init_db():
    try:
        conn = sqlite3.connect('gruppas.db', check_same_thread=False)
        conn.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, status TEXT)')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка БД: {e}")

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, 
        "🤖 **Gruppas AI Assistant запущен!**\n\n"
        "Я работаю на внутренней логике **Gruppas community**.\n"
        "• Напиши команду `/help`, чтобы узнать мои возможности.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['help'])
def help_cmd(m):
    bot.reply_to(m, 
        "🛠 **Доступные команды и функции:**\n\n"
        "1. Спроси про создателя («Кто тебя создал?»)\n"
        "2. Получи шаблон кода (напиши: `код питон` или `код с++`)\n"
        "3. Общайся, используя ключевое слово **группас** в чатах.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    if not m.text: 
        return
    
    is_private = m.chat.type == 'private'
    has_trigger = "группас" in m.text.lower()
    
    if is_private or has_trigger:
        try:
            bot.send_chat_action(m.chat.id, 'typing')
            clean_text = re.sub(r'(?i)группас', '', m.text).strip().lower()
            
            if not clean_text:
                bot.reply_to(m, "Слушаю? Задай свой вопрос или напиши запрос по коду.")
                return
            
            if any(w in clean_text for w in ["кто тебя создал", "создатель", "кто разработчик", "who created you"]):
                bot.reply_to(m, "🤖 Я — официальный ИИ-ассистент, разработанный и поддерживаемый **Gruppas community**!")
                return

            if "код" in clean_text and ("питон" in clean_text or "python" in clean_text):
                bot.reply_to(m, "🐍 **Пример скрипта на Python от Gruppas:**\n\n```python\ndef main():\n    print('Gruppas system active!')\n\nif __name__ == '__main__':\n    main()\n```", parse_mode="Markdown")
                return

            if "код" in clean_text and ("с++" in clean_text or "cpp" in clean_text):
                bot.reply_to(m, "⚙️ **Пример структуры на C++ от Gruppas:**\n\n```cpp\n#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"Gruppas C++ Engine Ready!\" << endl;\n    return 0;\n}\n```", parse_mode="Markdown")
                return

            bot.reply_to(m, f"📝 Запрос принят системой Gruppas: «{clean_text}». Все системы работают стабильно!")
            
        except Exception as e:
            print(f"Ошибка: {e}")

@server.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route('/')
def ping():
    return "Gruppas Internal Bot is running!", 200

if __name__ == "__main__":
    init_db()
    if RAILWAY_STATIC_URL:
        url = f"https://{RAILWAY_STATIC_URL}".strip('/')
        bot.remove_webhook()
        bot.set_webhook(url=f"{url}/{BOT_TOKEN}")
        print(f"--- ВЕБХУК УСПЕШНО УСТАНОВЛЕН НА: {url} ---")
    else:
        print("⚠️ Публичный домен Railway не найден.")

    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)
