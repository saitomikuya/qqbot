import random

class Plugin:
    def __init__(self, bot):
        self.bot = bot
        self.target_qqs = ['252737224', '601904795', '136208872', '1318242449']  # 要复读消息的QQ号列表

    async def handle_message(self, data):
        # 解析消息内容
        message_content = data['raw_message']
        group_id = data['group_id']
        sender_qq = str(data['user_id'])

        if sender_qq in self.target_qqs:
            # 检查消息是否为纯文字且长度小于100个字符，并且有20%的概率复读
            if len(message_content) < 100 and random.random() < 0.2:
                await self.bot.send_group_message(group_id, message_content)
