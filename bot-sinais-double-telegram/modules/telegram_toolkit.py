import telethon
from telethon.sync import TelegramClient, events
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.errors.rpcerrorlist import PhoneNumberBannedError
from telethon.tl.functions.channels import DeleteMessagesRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser

import asyncio
import sys

class TelegramBot:

    def __init__(self, phone_number):
        self.api_id = 10662829
        self.api_hash = "38bdd213b2ed9ea288d998709720136e"
        self.phone_number = phone_number
        self.client = TelegramClient(self.phone_number, self.api_id, self.api_hash)
        self.auth()

    def auth(self):        
        self.client.connect()
        if not self.client.is_user_authorized():
            try:
                self.client.send_code_request(self.phone_number)
                code = input(f'Codigo de login recebio no telegram: ')
                self.client.sign_in(self.phone_number, code)
            except PhoneNumberBannedError:
                print(f'{self.phone_number} is banned!')
                sys.exit(1)

    async def get_groups(self):
        chats = []
        last_date = None
        chunk_size = 200
        groups=[]

        result = await self.client(GetDialogsRequest(
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

    async def send_message(self, group, message):  
        try:
            group_entity = InputPeerChannel(group['id'], group['hash'])
            await self.client.send_message(group_entity, message)
        except:
            print(f"Error to send message to {group['title']}")

    async def get_channel_messages(self, group):
        group_entity = InputPeerChannel(group['id'], group['hash'])
        return await self.client.get_messages(group_entity)

    async def delete_channel_messages(self, group, msg_id):
        group_entity = InputPeerChannel(group['id'], group['hash'])
        await self.client.delete_messages(entity=group_entity, message_ids=[msg_id])

    async def reply_channel_message(self, group, msg_id, message):
        group_entity = InputPeerChannel(group['id'], group['hash'])
        await self.client.send_message(group_entity, message, reply_to=msg_id)

    async def edit_channel_message(self, group, msg_id, message):
        group_entity = InputPeerChannel(group['id'], group['hash'])
        await self.client.edit_message(group_entity, msg_id, text=message)






















