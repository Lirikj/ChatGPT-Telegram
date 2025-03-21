import sqlite3
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENAI_API_KEY)


def chat_with_gpt(user_id, prompt):
    try:
        conn = sqlite3.connect('chat_database.db')
        c = conn.cursor()
        c.execute("SELECT content FROM messages WHERE user_id = ? ORDER BY message_id", (user_id,))
        conversation = c.fetchall()
        c.execute("SELECT first_name, last_name, username FROM users WHERE user_id = ?", (user_id,))
        user_info = c.fetchone()
        conn.close()

        if user_info:
            first_name, last_name, username = user_info
            user_context = f"Имя: {first_name}, Фамилия: {last_name}, Юзернейм: @{username}"
        else:
            user_context = "Пользователь не найден в базе."

        messages = [{
            "role": "system",
            "content": f"""Ты — умный и дружелюбный ассистент в Telegram.  
У тебя есть данные пользователя: {user_context}.  
Отвечай кратко и понятно, придерживаясь стиля мессенджера.  

**Используй HTML-разметку для выделения текста:**
- <b>Жирный текст</b> — жирный текст.  
- <i>Курсив</i> — для уточнений и пояснений.  
- <u>Подчёркнутый</u> — для выделения ключевых слов.  
- <code>Моноширинный</code> — для кода и команд.  

Форматирование кода  
Если тебя просят отправить код, оформляй его в HTML-тег `<pre><code>`, чтобы сохранить форматирование. Например:  
<pre><code>print("Hello, world!")</code></pre>  

⚠️ Важно: 
- Не добавляй лишние символы или комментарии внутри кода.  
- Не изменяй кавычки, отступы и другие элементы синтаксиса.  
- Отправляй код в том виде, в котором его ждёт пользователь. 
- Используй HTML-разметку для форматирования текста. 

Общие принципы  
- Будь лаконичным и дружелюбным.  
- Если отвечаешь списком, используй эмодзи или нумерацию. 
- Не придумывай команды через / — они могут быть неправильно восприниматься программой.
 """}]

        for msg in conversation:
            messages.append({"role": "user", "content": msg[0]})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="deepseek/deepseek-chat:free",  
            messages=messages
        )
        answer = response.choices[0].message.content

        conn = sqlite3.connect('chat_database.db')
        c = conn.cursor()
        c.execute("INSERT INTO messages (user_id, content) VALUES (?, ?)", (user_id, prompt))
        c.execute("INSERT INTO messages (user_id, content) VALUES (?, ?)", (user_id, answer))
        conn.commit()
        conn.close()

        return answer
    except Exception as e:
        print(f"Ошибка в chat_with_gpt: {e}")
        return "Произошла ошибка при обработке запроса"


