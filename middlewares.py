from aiogram import BaseMiddleware
import time
from collections import defaultdict

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit=5, interval=60):
        super().__init__()
        self.limit = limit
        self.interval = interval
        self.user_timestamps = defaultdict(list)

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        now = time.time()
        timestamps = self.user_timestamps[user_id]

        timestamps = [t for t in timestamps if now - t < self.interval]
        timestamps.append(now)

        if len(timestamps) > self.limit:
            await event.answer("Слишком много запросов! Подождите немного ⏳")
            return

        self.user_timestamps[user_id] = timestamps
        return await handler(event, data)
