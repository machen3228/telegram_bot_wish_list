import asyncio
import json
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ContentType, ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from .config import settings

logging.basicConfig(level=logging.INFO)

bot = Bot(settings.bot_token)
dp = Dispatcher()


@dp.message()  # type: ignore[misc]
async def start(message: types.Message) -> None:
    web_app_info = types.WebAppInfo(url=settings.app_url)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Отправить данные', web_app=web_app_info))

    await message.answer(text='Привет!', reply_markup=builder.as_markup())


@dp.message(F.content_type == ContentType.WEB_APP_DATA)  # type: ignore[misc]
async def parse_data(message: types.Message) -> None:
    data = json.loads(message.web_app_data.data)
    await message.answer(
        f'<b>{data["title"]}</b>\n\n<code>{data["desc"]}</code>\n\n{data["text"]}', parse_mode=ParseMode.HTML
    )


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
