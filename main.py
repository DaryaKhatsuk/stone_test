import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters.command import Command
from config import botkey
from parsing_wb import sku_info


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
    result = f"Негативный отзыв: название товара:{product_info['product_name']}\n" \
             f"SKU товара: {product_info['sku']}\nРейтинг: {product_info['review_stars']}\n" \
             f"Текст отзыва: {product_info['review_text']}\n" \
             f"Рейтинг товара: {product_info['product_rating']}."

    await bot.send_message(chat_id='1069539543', text=result, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command('start'))
async def welcome(message):
    await bot.send_message(message.chat.id, f'Здравствуйте, *{message.from_user.first_name},* бот работает\n'
                                            f'ожидайте проверок отзывов с периодичностью в 5 минут', parse_mode='Markdown')


@dp.message(F.text)
async def run_parser_and_notify(message: types.Message):
    try:
        # Вызов агрегации данных
        result = await sku_info()
        # Отправка ответа пользователю
        test_res = [{
                            'sku': 'sku',
                            'product_name': 'product_name',
                            'product_rating': 'product_rating',

                            'review_text': 'review_text',
                            'review_stars': 'review_stars',
                        }]
        # Получение данных
        product_infos = await sku_info()

        # Отправка данных в Telegram
        for product_info in test_res:
            await send_data_to_telegram_bot(product_info)
    except Exception as e:
        await message.reply(f'Error: {e}')


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
