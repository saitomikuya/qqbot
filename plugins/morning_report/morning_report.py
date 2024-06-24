import aiohttp
import os

class MorningReportPlugin:
    def __init__(self, bot):
        self.bot = bot
        self.plugin_dir = os.path.dirname(__file__)
        self.api_url = "http://dwz.2xb.cn/zaob"
        self.image_dir = os.path.join(self.plugin_dir, 'images')
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

    async def handle_message(self, data):
        message_content = data['raw_message']
        group_id = data['group_id']
        
        if message_content == '早报':
            await self.send_morning_report(group_id)

    async def send_morning_report(self, group_id):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result['code'] == 200:
                            image_url = result['imageUrl']
                            datatime = result['datatime']
                            image_path = os.path.join(self.image_dir, f'{datatime}.png')

                            if os.path.exists(image_path):
                                # 如果图片已经存在，直接发送已保存的图片
                                await self.bot.send_group_message(group_id, f'[CQ:image,file=file:///{image_path}]')
                            else:
                                # 否则下载图片并发送
                                await self.download_image(image_url, image_path)
                                await self.bot.send_group_message(group_id, f'[CQ:image,file=file:///{image_path}]')
                        else:
                            await self.bot.send_group_message(group_id, f"API 返回错误: {result['msg']}")
                    else:
                        await self.bot.send_group_message(group_id, f"请求 API 失败，状态码: {response.status}")
        except Exception as e:
            await self.bot.send_group_message(group_id, f"获取早报时出错: {e}")

    async def download_image(self, url, path):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(path, 'wb') as f:
                            f.write(await response.read())
                    else:
                        raise Exception(f"下载图片失败，状态码: {response.status}")
        except Exception as e:
            raise Exception(f"下载图片时出错: {e}")
