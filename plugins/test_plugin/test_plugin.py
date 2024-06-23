class TestPlugin:
    def __init__(self, bot):
        self.bot = bot

    async def handle_message(self, data):
        message_content = data['raw_message']
        group_id = data['group_id']      
        if message_content == 'test':
            await self.bot.send_group_message(group_id, 'OK')
