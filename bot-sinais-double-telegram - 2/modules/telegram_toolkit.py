from telethon.sync import TelegramClient, events
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.errors.rpcerrorlist import PhoneNumberBannedError
from telethon.tl.functions.channels import DeleteMessagesRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser

import asyncio
import sys


def build_client(phone):
    api_id = 10662829
    api_hash = "38bdd213b2ed9ea288d998709720136e"
    phone_number = phone
    client = TelegramClient(phone_number, api_id, api_hash)
    client.connect()
    if not client.is_user_authorized():
        try:
            client.send_code_request(phone_number)
            code = input(f'Codigo de login recebio no telegram: ')
            client.sign_in(phone_number, code)
        except PhoneNumberBannedError:
            print(f'{phone_number} is banned!')
            sys.exit(1)
    print("Connected to telegram!")
    return client

async def get_groups(client):
    chats = []
    last_date = None
    chunk_size = 200
    groups=[]

    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash = 0
    ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            group_data = {}
            group_data['username'] = chat.username
            group_data['id'] = chat.id
            group_data['hash'] = chat.access_hash
            group_data['title'] = chat.title
            groups.append(group_data)
        except:
            continue
    return groups

async def send_message(client, group, message):  
    try:
        group_entity = InputPeerChannel(group['id'], group['hash'])
        await client.send_message(group_entity, message, parse_mode="html", link_preview=False)
    except:
        print(f"Error to send message to {group['title']}")

async def get_channel_messages(client, group):
    group_entity = InputPeerChannel(group['id'], group['hash'])
    return await client.get_messages(group_entity)

async def delete_channel_messages(client, group, msg_id):
    group_entity = InputPeerChannel(group['id'], group['hash'])
    await client.delete_messages(entity=group_entity, message_ids=[msg_id])

async def reply_channel_message(client, group, msg_id, message):
    group_entity = InputPeerChannel(group['id'], group['hash'])
    await client.send_message(group_entity, message, reply_to=msg_id)

async def edit_channel_message(client, group, msg_id, message):
    group_entity = InputPeerChannel(group['id'], group['hash'])
    await client.edit_message(group_entity, msg_id, text=message)





















