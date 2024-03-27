import asyncio
import logging
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters.command import Command
from config import botkey

# storage = MemoryStorage()  # FSM
logging.basicConfig(
    # указываем название с логами
    filename='log.txt',
    # указываем уровень логирования
    level=logging.INFO,
    # указываем формат сохранения логов
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s '
           u'[%(asctime)s] %(message)s')
bot = Bot(token=botkey)
dp = Dispatcher()


# Функция для отправки данных в Telegram
async def send_data_to_telegram_bot(product_info):
    result = f"Негативный отзыв:\nназвание товара:{product_info['product_name']}\n" \
             f"SKU товара: {product_info['sku']}\nРейтинг: {product_info['review_stars']}\n" \
             f"Текст отзыва: {product_info['review_text']}\n" \
             f"Рейтинг товара: {product_info['product_rating']}."

    await bot.send_message(chat_id='YOUR_CHAT_ID', text=result, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command('start'))
async def welcome(message):
    await bot.send_message(message.chat.id, f'Здравствуйте, *{message.from_user.first_name},* бот работает\n'
                                            f'ожидайте проверок отзывов с периодичностью в 5 минут', parse_mode='Markdown')
    while True:
        await run_parser_and_notify()
        time.sleep(300)

@dp.message(F.text)
async def run_parser_and_notify():
    try:
        # Получение данных
        from parsing_wb import sku_info
        product_infos = await sku_info()

        # Отправка данных в Telegram
        for product_info in product_infos:
            await send_data_to_telegram_bot(product_info)
    except:
        pass


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
