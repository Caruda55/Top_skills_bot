import asyncio
import handlers

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from config import Config, load_config


# Функция конфигурирования и запуска бота
async def main() -> None:

    # Инициализируем бот и диспетчер
    config: Config = load_config()
    bot: Bot = Bot(token=config.tg_bot.token, 
                   parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(handlers.router)
    #print('Бот активен')
    

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    

if __name__ == '__main__':
    asyncio.run(main())
