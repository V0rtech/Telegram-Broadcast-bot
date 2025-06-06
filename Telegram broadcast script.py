from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import asyncio
import sys
import re
import random

# ---- SETUP: Replace these with your real details ----
api_id = 'Input API ID' 
api_hash = 'Input API Hash'

# ---- GATHER USER INPUT ----

def get_user_list():
    print("Enter usernames (with or without @), user IDs, or phone numbers (in international format). Type 'done' when finished:")
    users = []
    while True:
        u = input("> ").strip()
        if u.lower() == 'done':
            break
        if not u:
            continue  # skip empty lines

        # Check if it's a phone number (e.g., +1234567890)
        if re.match(r'^\+\d{6,15}$', u):
            users.append(u)
            continue

        # Check if it's a numeric user ID
        try:
            u_int = int(u)
            users.append(u_int)
            continue
        except ValueError:
            pass

        # Treat as username, add '@' if not present
        if not u.startswith("@"):
            u = "@" + u
        users.append(u)

    if not users:
        print("You must enter at least one user. Exiting.")
        sys.exit(1)
    return users

def get_message():
    print("\nType the message to send (end with a blank line):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    msg = "\n".join(lines).strip()
    if not msg:
        print("You must enter a non-empty message. Exiting.")
        sys.exit(1)
    return msg

async def import_phone_and_get_user(client, phone_number):
    contact = InputPhoneContact(client_id=0, phone=phone_number, first_name="Temp", last_name="Contact")
    result = await client(ImportContactsRequest([contact]))
    if result.users:
        return result.users[0]
    else:
        print(f"❌ No Telegram user found for {phone_number} or they don't allow unknown users to send them messages")
        return None

async def main():
    users = get_user_list()
    msg = get_message()

    async with TelegramClient('userbot_session', api_id, api_hash) as client:
        print("\nSending messages...")
        for i, user in enumerate(users):
            try:
                if isinstance(user, str) and user.startswith('+'):
                    # It's a phone number, resolve it
                    resolved_user = await import_phone_and_get_user(client, user)
                    if resolved_user:
                        await client.send_message(resolved_user, msg)
                        print(f"Sent to {user}")
                    else:
                        print(f"Failed for {user}")
                else:
                    await client.send_message(user, msg)
                    print(f"Sent to {user}")
                
                # Add random delay between messages (except after the last one)
                if i < len(users) - 1:
                    delay = random.uniform(3, 5)
                    print(f"Waiting {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                print(f"Failed for {user}: {e}")

if __name__ == "__main__":
    asyncio.run(main())