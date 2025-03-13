import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from handlers import register_handlers  # Импортируем функцию регистрации обработчиков

async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Starting bot...')

    # Создаём бота и диспетчер
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    # Добавляем бота в контекст (чтобы он был доступен в обработчиках)
    dp["bot"] = bot

    # Регистрируем обработчики
    register_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
