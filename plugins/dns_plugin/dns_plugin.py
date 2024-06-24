import dns.resolver
import asyncio

class DNSPlugin:
    def __init__(self, bot):
        self.bot = bot

    async def handle_message(self, data):
        message_content = data['raw_message']
        group_id = data['group_id']
        message_id = data['message_id']
        
        if message_content.startswith('dns '):
            domain = message_content.split(' ', 1)[1]
            response = await self.query_dns(domain)
            await self.bot.send_group_message(group_id, f"[CQ:reply,id={message_id}] {response}")

    async def query_dns(self, domain):
        records = {
            'NS': [],
            'A': [],
            'CNAME': [],
            'MX': []
        }
        try:
            for record_type in records.keys():
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    records[record_type] = [rdata.to_text() for rdata in answers]
                except dns.resolver.NoAnswer:
                    records[record_type] = []
                except dns.resolver.NXDOMAIN:
                    return f"域名 {domain} 不存在"
                except Exception as e:
                    return f"查询 {domain} 的 {record_type} 记录时出错: {e}"

            response = f"【{domain} DNS查询】\n"
            for record_type, values in records.items():
                if values:
                    response += f"{record_type}记录：\n" + "\n".join(values) + "\n\n"
            return response.strip()
        except Exception as e:
            return f"查询 {domain} 的 DNS 记录时出错: {e}"
