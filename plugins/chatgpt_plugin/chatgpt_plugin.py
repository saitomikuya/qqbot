import aiohttp
import asyncio

class Plugin:
    def __init__(self, bot):
        self.bot = bot

        # Azure OpenAI API
        self.azure_url = 'https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME'
        self.azure_api_key = 'YOUR_API_KEY'
        self.azure_api_version = '2024-02-01'
        self.model = 'gpt-4o-2024-05-13'  # 部署的模型版本名称

        # Google Gemini API
        self.api_key = 'YOUR_API_KEY'
        self.api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

    async def handle_message(self, data):
        message_content = data['raw_message']
        group_id = data['group_id']
        user_id = data['user_id']
        message_id = data['message_id']  # 获取消息ID
        at_qq = f'[CQ:at,qq={self.bot.qq}]'

        if message_content.startswith(at_qq):
            question = message_content.replace(at_qq, '').strip()
            if question:
                # 创建异步任务来处理响应
                asyncio.ensure_future(self.process_question(group_id, message_id, question))

    async def process_question(self, group_id, message_id, question):
        #answer = await self.get_chatgpt_response(question)
        answer = await self.get_gemini_response(question)
        if answer:
            response_message = f'[CQ:reply,id={message_id}] {answer}'
            await self.bot.send_group_message(group_id, response_message)

    async def get_chatgpt_response(self, question):
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.azure_api_key
        }
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': question}
            ]
        }
        url = f"{self.azure_url}/chat/completions?api-version={self.azure_api_version}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        return f"调用ChatGPT接口失败，状态码: {response.status}"
            except Exception as e:
                return f"调用ChatGPT接口时出错: {e}"
        return None

    async def get_gemini_response(self, question):
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': question
                        }
                    ]
                }
            ]
        }
        url = f'{self.api_url}?key={self.api_key}'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    candidates = result.get('candidates', [])
                    if candidates:
                        return candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '无法获取答案')
                    else:
                        return '无法获取答案'
                else:
                    return '无法连接到Google Gemini API'
