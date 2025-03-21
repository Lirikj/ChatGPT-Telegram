import time 
import requests
from telebot import types
from config import bot 
from chatGPT import chat_with_gpt
from baza import init_db, clear_database, add_user


@bot.message_handler(commands=['start', 'menu'])
def menu(message): 
    user_id = message.chat.id 
    username = message.from_user.username if message.from_user.username else ''
    first_name = message.from_user.first_name 
    last_name = message.from_user.last_name if message.from_user.last_name else ''
    add_user(user_id, username, first_name, last_name)
    bot.send_message(message.chat.id, f'Привет, {first_name} {last_name} \n'
                    '\nЯ нейросеть EurekaGPT, чем могу помочь?') 


@bot.message_handler(commands=['info']) 
def info(message): 
    bot.send_message(message.chat.id, 'EurekaGPT 1.3 \n'
                    '\n🧑🏼‍💻developer - @abamma'
                    '\n🤖Бот использует нейросеть deepseek R1 для общения с пользователем')  


@bot.message_handler(commands=['admin']) 
def admin(message):
    user_id = message.chat.id 

    markup = types.InlineKeyboardMarkup()
    polz_btn = types.InlineKeyboardButton(text='Пользователи', callback_data='users')
    markup.add(polz_btn)

    if user_id == 485547989: 
        bot.send_message(user_id, 'Привет, администратор! \n'
                        '\nВы вошли в режим администратора', reply_markup=markup) 
    else:
        bot.send_message(user_id, 'У вас нет доступа к админ-панели')


@bot.message_handler(commands=['clear'])
def clear_memory(message):
    try:
        clear_database(message.chat.id)
        bot.send_message(message.chat.id, "Память очищена")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при очистке памяти")
        print(f"Ошибка в clear_memory: {e}")


@bot.message_handler(content_types=['text']) 
def gpt_response(message): 
    try:
        user_id = message.chat.id 
        username = message.from_user.username if message.from_user.username else ''
        first_name = message.from_user.first_name 
        last_name = message.from_user.last_name if message.from_user.last_name else ''
        add_user(user_id, username, first_name, last_name)

        bot.send_chat_action(message.chat.id, 'typing')  
        text = message.text
        response = chat_with_gpt(user_id, text)

        max_length = 4096
        if len(text) <= max_length:
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        else:
            for i in range(0, len(text), max_length):
                bot.send_message(message.chat.id, response[i:i+max_length], parse_mode='HTML')

    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позже")
        print(f"Ошибка в gpt_response: {e}")


@bot.callback_query_handler(func=lambda call: call.data == 'users')
def users(callback):
    try:
        import sqlite3
        conn = sqlite3.connect('chat_database.db')
        c = conn.cursor()
        c.execute("SELECT user_id, first_name, last_name, username FROM users")
        rows = c.fetchall()
        conn.close()
        
        if rows:
            text = ""
            for i, (user_id, first_name, last_name, username) in enumerate(rows, 1):
                text += f"{i}. <a href='tg://openmessage?user_id={user_id}'>{first_name} {last_name}</a> @{username}\n"
            max_length = 4096
            if len(text) <= max_length:
                bot.send_message(callback.message.chat.id, text, parse_mode='HTML')
            else:
                for i in range(0, len(text), max_length):
                    bot.send_message(callback.message.chat.id, text[i:i+max_length], parse_mode='HTML')
        else:
            bot.send_message(callback.message.chat.id, "Пользователи не найдены.")
    except Exception as e:
        bot.send_message(callback.message.chat.id, "Ошибка при получении пользователей.")
        print(f"Ошибка в list_users: {e}")


init_db()
while True:
    try:
        bot.polling(none_stop=True, timeout=90)
    except requests.exceptions.ReadTimeout:
        print("⏳ ReadTimeout! Перезапускаю polling...")
        time.sleep(5)  
    except Exception as e:
        print(f"Ошибка в bot.polling: {e}")
        time.sleep(5)