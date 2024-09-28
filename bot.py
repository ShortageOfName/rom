import time
import subprocess
import os
from telethon import TelegramClient, events, Button

# File to store user data
USER_DATA_FILE = 'users.txt'

Apid = 22157690
Apihash = "819a20b5347be3a190163fff29d59d81"
tken = "7483201528:AAGLZzUEMYYN-wYmYUUwD8eVOQyiflG8-d4"
SEMXUSER = 2092103173

client = TelegramClient('R5O60D', Apid, Apihash).start(bot_token=tken)

# Load users from the text file
def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    
    with open(USER_DATA_FILE, 'r') as f:
        return {int(user_id): username for user_id, username in (line.strip().split(',') for line in f)}

# Save users to the text file
def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        for user_id, username in users.items():
            f.write(f"{user_id},{username}\n")

# Check if the user is authorized
def is_authorized(user_id, users):
    return user_id in users

users = load_users()

@client.on(events.NewMessage(pattern=r'#b (\S+) (\d+) (\d+)'))
async def handle_bgmi(event):
    user_id = event.sender_id
    if not is_authorized(user_id, users):
        await event.reply("**You are not authorized to use this command.**")
        return

    target, port, time_ = event.pattern_match.groups()

    buttons = [
        [Button.inline("Start", data=f'start_{target}_{port}_{time_}'),
         Button.inline("Stop", data=f'stop_{target}_{port}_{time_}')]
    ]
    
    await event.reply("Control BGMI execution:", buttons=buttons)

@client.on(events.CallbackQuery(pattern=b'start_(\\S+)_(\\d+)_(\\d+)'))
async def start_bgmi(event):
    target, port, time_ = event.data.decode().split('_')[1:]
    command = f'./bgmi {target} {port} {time_} 200'
    
    try:
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await event.answer("BGMI started.", alert=True)
    except Exception as e:
        await event.answer(f"Error: {str(e)}", alert=True)

@client.on(events.CallbackQuery(pattern=b'stop_(\\S+)_(\\d+)_(\\d+)'))
async def stop_bgmi(event):
    target, port, time_ = event.data.decode().split('_')[1:]
    command_pattern = f'./bgmi {target} {port} {time_} 200'
    
    try:
        subprocess.Popen(f'pkill -f "{command_pattern}"', shell=True)
        await event.answer("BGMI process stopped.", alert=True)
    except Exception as e:
        await event.answer(f"Error: {str(e)}", alert=True)

@client.on(events.NewMessage(pattern='/add'))
async def add(event):
    if event.sender_id != SEMXUSER:
        await event.reply("**You are not authorized to use this command.**")
        return
    try:
        _, Infouser = event.message.message.split()
        user_id = Infouser if Infouser.isdigit() else None
        if user_id is None:
            user = await client.get_entity(Infouser)
            user_id = user.id
        
        users[user_id] = Infouser
        save_users(users)
        await event.reply(f"**Added {Infouser} to authorized users.**")
    except Exception as e:
        await event.reply(f"Error: {str(e)}")

@client.on(events.NewMessage(pattern='/remove'))
async def remove(event):
    if event.sender_id != SEMXUSER:
        await event.reply("**You are not authorized to use this command.**")
        return
    try:
        _, Infouser = event.message.message.split()
        user_id = Infouser if Infouser.isdigit() else None
        if user_id is None:
            user = await client.get_entity(Infouser)
            user_id = user.id
        
        if user_id in users:
            del users[user_id]
            save_users(users)
            await event.reply(f"**Removed {Infouser} from authorized users.**")
        else:
            await event.reply("User not found.")
    except Exception as e:
        await event.reply(f"Error: {str(e)}")

client.start()
client.run_until_disconnected()
  
