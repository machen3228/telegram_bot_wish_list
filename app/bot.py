# mypy: disable-error-code="misc"
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.types import MenuButtonWebApp
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

bot = Bot(settings.bot_token)
dp = Dispatcher()
router = Router()
dp.include_router(router)


async def set_menu_button(user_id: int) -> None:
    menu_button = MenuButtonWebApp(
        text='📱 Открыть App',
        web_app=types.WebAppInfo(url=settings.app_url),
    )
    await bot.set_chat_menu_button(chat_id=user_id, menu_button=menu_button)


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    user = message.from_user
    logger.info('User %s started bot', user.id)
    await set_menu_button(user.id)
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='📱 Открыть Mini App',
            web_app=types.WebAppInfo(url=settings.app_url),
        )
    )

    await message.answer(
        '👋 Привет!\n\nНажмите кнопку ниже, чтобы открыть Mini App.\nТакже кнопка доступна в меню бота.',
        reply_markup=builder.as_markup(),
    )


@router.message()
async def fallback_handler(message: types.Message) -> None:
    await message.answer('Для открытия приложения используйте команду /start')


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped')
