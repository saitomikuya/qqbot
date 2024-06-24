import re
import aiohttp
import socket
import json

class IPInfoPlugin:
    def __init__(self, bot):
        self.bot = bot

    async def handle_message(self, data):
        message_content = data['raw_message']
        group_id = data['group_id']
        message_id = data['message_id']

        # 检查消息格式是否为 "ip domain.com" 或 "ip 8.8.8.8"
        match = re.match(r'^ip\s+([^\s]+)', message_content)
        if match:
            query = match.group(1)
            if self.is_valid_ipv4(query):
                ip = query
            elif self.is_valid_ipv6(query):
                await self.bot.send_group_message(group_id, f"[CQ:reply,id={message_id}] 暂不支持IPv6查询：{query}")
                return
            else:
                ip = self.resolve_domain_to_ip(query)
                if not ip:
                    await self.bot.send_group_message(group_id, f"[CQ:reply,id={message_id}] 无法解析域名：{query}")
                    return

            # 查询 IP 信息
            ip_info = await self.get_ip_info(ip)
            if ip_info:
                response_message = (
                    f"[CQ:reply,id={message_id}] 【{query} IP查询】\n"
                    f"IP地址：{ip_info.get('IP', '未知')}\n"
                    f"ISP信息：{ip_info.get('ISP', '未知')}\n"
                    f"位置信息：{ip_info.get('Location', '未知')}"
                )
                await self.bot.send_group_message(group_id, response_message)
            else:
                await self.bot.send_group_message(group_id, f"[CQ:reply,id={message_id}] 无法获取IP信息：{ip}")

    def is_valid_ipv4(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def is_valid_ipv6(self, ip):
        try:
            socket.inet_pton(socket.AF_INET6, ip)
            return True
        except socket.error:
            return False

    def resolve_domain_to_ip(self, domain):
        try:
            return socket.gethostbyname(domain)
        except socket.error:
            return None

    async def get_ip_info(self, ip):
        url = f"https://lib.mk/{ip}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        try:
                            text = await response.text()
                            ip_info = json.loads(text)  # 使用 JSON 解析
                            return ip_info
                        except json.JSONDecodeError:
                            return None
                    else:
                        return None
        except Exception:
            return None
