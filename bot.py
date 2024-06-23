import asyncio
import websockets
import json
import config
import importlib
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QQBot:
    def __init__(self):
        self.qq = config.BOT_QQ
        self.ws_server = config.WS_SERVER
        self.plugins = []
        self.websocket = None
        self.send_queue = asyncio.Queue()
        self.recv_queue = asyncio.Queue()

    async def connect(self):
        while True:
            try:
                async with websockets.connect(self.ws_server) as websocket:
                    self.websocket = websocket
                    logging.info("连接到 WebSocket 服务器成功")
                    await asyncio.gather(
                        self.listen_messages(),
                        self.send_messages(),
                        self.process_messages()
                    )
            except Exception as e:
                logging.error(f"连接错误: {e}")
                await asyncio.sleep(5)

    async def listen_messages(self):
        try:
            async for message in self.websocket:
                await self.recv_queue.put(message)
        except websockets.ConnectionClosed:
            logging.warning("连接关闭，尝试重新连接...")
        except Exception as e:
            logging.error(f"监听消息时出错: {e}")

    async def send_messages(self):
        while True:
            payload = await self.send_queue.get()
            try:
                await asyncio.wait_for(self.websocket.send(json.dumps(payload)), timeout=10)
            except asyncio.TimeoutError:
                logging.error("发送消息超时")
            except Exception as e:
                logging.error(f"发送消息时出错: {e}")

    async def process_messages(self):
        while True:
            message = await self.recv_queue.get()
            await self.handle_message(message)

    async def handle_message(self, message):
        try:
            data = json.loads(message)
            if data.get('post_type') == 'message' and data.get('message_type') == 'group':
                # 群消息
                group_info = await self.get_group_info(data.get('group_id'))
                group_name = group_info['data']['group_name']
                #print(f"[{group_name}]{data.get('sender', {}).get('nickname')}({data.get('user_id')}):{data.get('raw_message')}")
                for plugin in self.plugins:
                    if hasattr(plugin, 'handle_message'):
                        await plugin.handle_message(data)
            elif data.get('post_type') == 'notice' and data.get('notice_type') == 'group_recall':
                # 群消息撤回通知
                for plugin in self.plugins:
                    if hasattr(plugin, 'handle_recall'):
                        try:
                            await plugin.handle_recall(data)
                        except Exception as e:
                            logging.error(f"处理撤回消息时出错: {e}")
        except Exception as e:
            logging.error(f"处理消息时出错: {e}")

    def load_plugins(self):
        # 加载插件
        plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        for plugin_name in os.listdir(plugins_dir):
            plugin_path = os.path.join(plugins_dir, plugin_name)
            if os.path.isdir(plugin_path) and '__init__.py' in os.listdir(plugin_path):
                try:
                    module = importlib.import_module(f'plugins.{plugin_name}')
                    self.plugins.append(module.Plugin(self))
                    logging.info(f"加载插件: {plugin_name}")
                except Exception as e:
                    logging.error(f"加载插件 {plugin_name} 时出错: {e}")

    async def send_group_message(self, group_id, message):
        # 发送群消息
        payload = {
            'action': 'send_group_msg',
            'params': {
                'group_id': group_id,
                'message': message
            }
        }
        await self.send_queue.put(payload)

    async def send_private_message(self, user_id, message):
        # 发送私聊消息
        payload = {
            'action': 'send_private_msg',
            'params': {
                'user_id': user_id,
                'message': message
            }
        }
        await self.send_queue.put(payload)

    async def get_group_info(self, group_id):
        # 获取群信息
        payload = {
            'action': 'get_group_info',
            'params': {
                'group_id': group_id
            }
        }
        await self.send_queue.put(payload)
        response = await self.recv_queue.get()       
        try:
            group_info = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("Received response is not valid JSON")       
        return group_info

    async def get_group_member_info(self, group_id, user_id):
        # 获取群成员信息
        payload = {
            'action': 'get_group_member_info',
            'params': {
                'group_id': group_id,
                'user_id': user_id
            }
        }
        await self.send_queue.put(payload)
        response = await self.recv_queue.get()
        try:
            member_info = json.loads(response)
            if member_info['status'] == 'ok':
                return member_info['data']
        except json.JSONDecodeError:
            logging.error("获取群成员信息时出错: 无效的 JSON 响应")
        except Exception as e:
            logging.error(f"获取群成员信息时出错: {e}")
        return None

    async def start(self):
        self.load_plugins()  # 加载所有插件
        await self.connect()  # 连接到WebSocket服务器并开始运行

if __name__ == '__main__':
    bot = QQBot()
    asyncio.run(bot.start())
