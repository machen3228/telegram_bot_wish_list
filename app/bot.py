# mypy: disable-error-code="misc"
import asyncio
import json
import urllib.parse

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.types import MenuButtonWebApp
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import settings

bot = Bot(settings.bot_token)
dp = Dispatcher()
router = Router()
dp.include_router(router)


async def get_user_profile_photo_url(user_id: int) -> str | None:
    photos = await bot.get_user_profile_photos(user_id)
    if photos.total_count > 0:
        last_photo_sizes = photos.photos[0]
        preview_photo = last_photo_sizes[0]
        file_info = await bot.get_file(preview_photo.file_id)
        return f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'
    return None


async def set_menu_button(user_id: int) -> None:
    menu_button = MenuButtonWebApp(
        text='📱 Открыть App',
        web_app=types.WebAppInfo(url=settings.app_url),  # Просто чистый URL
    )
    await bot.set_chat_menu_button(chat_id=user_id, menu_button=menu_button)


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    user_id = message.from_user.id
    user_data = {
        'user_id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'avatar_url': await get_user_profile_photo_url(user_id),
    }
    await set_menu_button(user_id)
    json_data = json.dumps(user_data)
    encoded_data = urllib.parse.quote(json_data)
    webapp_url = f'{settings.app_url}?user_data={encoded_data}'
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='📱 Открыть Mini App', web_app=types.WebAppInfo(url=webapp_url)))
    user_name = message.from_user.first_name or 'друг'
    if message.from_user.last_name:
        user_name = f'{message.from_user.first_name} {message.from_user.last_name}'
    await message.answer(
        f'👋 Привет, {user_name}!\n\n'
        f'Нажмите кнопку ниже, чтобы открыть Mini App.\n'
        f'Теперь кнопка доступна в меню бота - вы можете открывать приложение в любое время.',
        reply_markup=builder.as_markup(),
    )


@router.message()
async def fallback_handler(message: types.Message) -> None:
    await message.answer('👋 Для открытия приложения используйте команду /start')


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
