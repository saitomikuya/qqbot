import asyncio
import time

class DailyMessagePlugin:
    def __init__(self, bot):
        self.bot = bot
        self.group_id = 723609186  # 替换为要发送消息的 QQ 群号
        self.timezone_offset = 8 * 3600  # UTC+08:00
        asyncio.ensure_future(self.schedule_daily_messages())

    async def schedule_daily_messages(self):
        await asyncio.sleep(1)
        asyncio.ensure_future(self.schedule_utc("08:30:00", self.send_morning_message))
        asyncio.ensure_future(self.schedule_utc("23:30:00", self.send_night_message))

    async def schedule_utc(self, HMS, aFunc, *args):
        at = time.strptime(HMS, "%H:%M:%S")
        sec = at.tm_hour * 60 * 60 + at.tm_min * 60 + at.tm_sec - self.timezone_offset
        while True:
            n = int(time.time())
            t = n % 86400
            d = n - t + sec
            if d > n:
                delay = d - n
            elif d < n:
                delay = 86400 - t + sec
            else:
                delay = 0
            print(f"ScheduleDelay<{aFunc.__name__}>: {delay}", flush=True)
            await asyncio.sleep(delay)
            await aFunc(*args)
            await asyncio.sleep(1)

    async def send_morning_message(self):
        message = "早上好各位！如果你看到这条消息，说明虾佬的L8又度过了一个安全的夜晚！"
        await self.bot.send_group_message(self.group_id, message)

    async def send_night_message(self):
        message = "晚安各位！希望虾佬的L8能在夜里平安无事！"
        await self.bot.send_group_message(self.group_id, message)
