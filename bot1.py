import asyncio

import telebot
import json
from telethon import TelegramClient, events

TOKEN = "6725364063:AAHppfbYZ0NOz4PdZKbMERcvRbIi35tRAJs"
bot = telebot.TeleBot(TOKEN)

# Змінні для збереження налаштувань
channels_to_track = set()
admin_channel_id = 2015256496
data = {'posted_messages': []}

api_id = 22890952
api_hash = 'fbe4789f4fccabd20b303d1f1ea831b2'
phone_number = "+351960190648"

client = TelegramClient('session_name', api_id, api_hash)
client.start(phone_number)

def save_settings():
    settings = {'channels_to_track': list(channels_to_track)}
    with open('settings.json', 'w') as file:
        json.dump(settings, file)

def load_settings():
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
            channels_to_track.update(settings.get('channels_to_track', []))
    except FileNotFoundError:
        pass

def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file)

# Завантажуємо збережені налаштування
load_settings()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Я тут, щоб відстежувати канали за тобою. Використовуй /add_channel та /list_channels.")

@bot.message_handler(commands=['add_channel'])
def add_channel(message):
    msg = bot.reply_to(message, "Введи ім'я каналу (без '@'):")
    bot.register_next_step_handler(msg, process_channel_name)

def process_channel_name(message):
    try:
        channel_name = message.text
        channels_to_track.add(f'@{channel_name}')
        save_settings()
        bot.reply_to(message, f"Канал @{channel_name} додано до списку відстежуваних.")
    except Exception:
        bot.reply_to(message, 'Виникла помилка. Спробуйте ще раз.')

@bot.message_handler(commands=['list_channels'])
def list_channels(message):
    bot.reply_to(message, f"Відстежувані канали: {', '.join(channels_to_track)}")

async def process_message(message):
    text = message.text

    if text not in data['posted_messages']:
        for channel in channels_to_track:
            print(f"Forwarding message to channel {channel}")
            try:
                await client.send_message(admin_channel_id, text)
                print(f"Message forwarded successfully to channel {channel}")
            except Exception as e:
                print(f"Error forwarding message to channel {channel}: {e}")

        data['posted_messages'].append(text)
        save_data(data)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    asyncio.run(process_message(message))
    save_data(data)

if __name__ == "__main__":
    bot.polling(none_stop=True)
    client.run_until_disconnected()