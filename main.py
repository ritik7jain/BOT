import openai
import logging
import os
import random

import pymysql as pymysql
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Database connection details
DB_HOST = 'localhost'
DB_USERNAME = 'root'
DB_PASSWORD = 'jain8ritik123'
DB_NAME = 'users'

# Connect to the database
conn = pymysql.connect(host=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD, db=DB_NAME)
# Replace YOUR_API_KEY with your actual API key
openai.api_key = "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"

# Replace YOUR_TELEGRAM_TOKEN with your actual Telegram token
updater = Updater(token="5905437737:AAHWHUF0P6d_P_2a8JRqNmh-dwYwPNqeHyc", use_context=True)
usage_counts = {}
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there! I'm Bot and can answer your all question feel free to ask any question")

def answer(update, context):
    chat_id = update.effective_chat.id

    # Check how many times the user has used the bot
    with conn.cursor() as cursor:
        cursor.execute("SELECT usage_count FROM jain WHERE chat_id=%s", (chat_id,))
        result = cursor.fetchone()

        if result is None:
            # This is the first time the user has used the bot, so insert a new record in the database
            cursor.execute("INSERT INTO jain (chat_id, usage_count) VALUES (%s, 1)", (chat_id,))
            conn.commit()
            context.bot.send_message(chat_id=chat_id, text="Welcome! You can use me 1 time for Demo.")
            question = update.message.text
            prompt = (f"Question: {question}\nAnswer: ")

            # Use the OpenAI API to generate an answer to the question
            completions = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=1024, n=1,
                                                   stop=None, temperature=0.5)
            answer = completions.choices[0].text
            answer = answer.strip().replace(prompt, "")

            context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
        else:
            # The user has used the bot before, so retrieve their usage count from the database
            usage_count = result[0]

            if usage_count > 0:
                # The user has not reached their usage limit, so decrement their usage count and send a message
                cursor.execute("UPDATE jain SET usage_count=%s WHERE chat_id=%s", (usage_count - 1, chat_id))
                conn.commit()
                context.bot.send_message(chat_id=chat_id,
                                         text="You can use me {} more times.".format(usage_count - 1))
                question = update.message.text
                prompt = (f"Question: {question}\nAnswer: ")

                # Use the OpenAI API to generate an answer to the question
                completions = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=2048, n=5,
                                                       stop=None, temperature=0.5)
                for choice in completions.choices:
                    answer = choice.text
                    answer = answer.strip().replace(prompt, "")
                    #print(answer)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

            else:
                # The user has reached their usage limit, so send a message indicating that they cannot use the bot anymore
                context.bot.send_message(chat_id=chat_id,
                                         text="Sorry, you have reached your usage limit, To use me again please contact admin.")



updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, answer))

updater.start_polling()
