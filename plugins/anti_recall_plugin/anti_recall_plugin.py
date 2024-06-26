import os
import re
import json
import logging
from datetime import datetime

class AntiRecallPlugin:
    def __init__(self, bot):
        self.bot = bot
        self.NOTIFY_QQ = 4499149 # 替换为你要接受撤回消息的QQ号
        self.messages = {}
        self.storage_path = os.path.join(os.path.dirname(__file__), 'messages.json')
        self.load_messages()

    def load_messages(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
        else:
            self.messages = {}

    def save_messages(self):
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=4)

    async def handle_message(self, data):
        if data.get('post_type') == 'message' and data.get('message_type') == 'group':
            group_id = str(data['group_id'])
            message_id = str(data['message_id'])
            user_id = str(data['user_id'])
            message_content = data['raw_message']

            if group_id not in self.messages:
                self.messages[group_id] = {}
            self.messages[group_id][message_id] = {
                'user_id': user_id,
                'message_content': message_content,
            }
            self.save_messages()

    async def handle_recall(self, data):
        if data.get('post_type') == 'notice' and data.get('notice_type') == 'group_recall':
            group_id = str(data['group_id'])
            operator_id = str(data['operator_id'])
            message_id = str(data['message_id'])

            if group_id in self.messages and message_id in self.messages[group_id]:
                recalled_message = self.messages[group_id].get(message_id)
                group_info = await self.bot.get_group_info(group_id)
                group_name = group_info['data']['group_name']
                user_id = recalled_message['user_id']
                operator_info = await self.bot.get_group_member_info(group_id, operator_id)
                recalled_user_info = await self.bot.get_group_member_info(group_id, user_id)

                # 使用群昵称，如果群昵称为空则使用QQ昵称
                operator_nickname = operator_info['card'] if operator_info and operator_info['card'] else operator_info['nickname'] if operator_info else operator_id
                recalled_user_nickname = recalled_user_info['card'] if recalled_user_info and recalled_user_info['card'] else recalled_user_info['nickname'] if recalled_user_info else user_id

                message_content = recalled_message['message_content']
                # 去掉私聊不支持的格式的内容
                message_content = re.sub(r'\[CQ:reply,id=[^\]]+\]', '', message_content)
                message_content = re.sub(r'\[CQ:at,qq=[^\]]+\]', '', message_content)
                if operator_id == user_id:
                    notify_message = f"{operator_nickname}({operator_id})在“{group_name}”群中撤回消息：{message_content}"
                else:
                    notify_message = f"{recalled_user_nickname}({user_id})在“{group_name}”群中被{operator_nickname}({operator_id})撤回消息：{message_content}"
                await self.bot.send_private_message(self.NOTIFY_QQ, notify_message)
