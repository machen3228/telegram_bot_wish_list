# mypy: disable-error-code="misc"
import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

bot = Bot(settings.bot_token)
dp = Dispatcher()
router = Router()
dp.include_router(router)

registered_users: dict[Any, Any] = {}


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id in registered_users:
        await open_mini_app(message, user_id)
    else:
        await send_welcome_message(message)


async def send_welcome_message(message: types.Message) -> None:
    welcome_text = '👋 Добро пожаловать!\n\nДля регистрации и доступа к боту, пожалуйста, отправьте свой контакт.'
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, keyboard=[[KeyboardButton(text='📱 Отправить мой контакт', request_contact=True)]]
    )
    await message.answer(welcome_text, reply_markup=keyboard)


async def open_mini_app(message: types.Message, user_id: int) -> None:
    web_app_info = types.WebAppInfo(url=settings.app_url)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='📱 Открыть Mini App', web_app=web_app_info))
    user_data = registered_users[user_id]
    user_name = user_data.get('name', 'пользователь')
    builder.add(types.KeyboardButton(text='🔄 Сменить профиль'))
    builder.adjust(1)
    await message.answer(
        f'Рады снова видеть вас, {user_name}!\n\nНажмите кнопку ниже, чтобы открыть Mini App:',
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@router.message(F.contact)
async def get_contact(message: types.Message) -> None:
    contact = message.contact
    user_id = message.from_user.id
    full_name_parts = []
    if contact.first_name:
        full_name_parts.append(contact.first_name)
    if contact.last_name:
        full_name_parts.append(contact.last_name)
    full_name = ' '.join(full_name_parts) if full_name_parts else 'Пользователь'
    registered_users[user_id] = {
        'id': user_id,
        'name': full_name,
        'phone': contact.phone_number,
        'registration_date': datetime.now(UTC).isoformat(),
    }
    logger.info(f'Новый пользователь зарегистрирован: {full_name}, телефон: {contact.phone_number}')
    await message.answer(
        f'✅ Регистрация успешна!\n\nДобро пожаловать, {full_name}!\nВаш номер: {contact.phone_number}',
        reply_markup=ReplyKeyboardRemove(),
    )
    await open_mini_app(message, user_id)


@router.message(F.text == '🔄 Сменить профиль')
async def change_profile(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id in registered_users:
        del registered_users[user_id]
        await message.answer(
            'Ваш профиль удален. Теперь вы можете зарегистрироваться заново.', reply_markup=ReplyKeyboardRemove()
        )
    await send_welcome_message(message)


@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def parse_data(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id not in registered_users:
        await message.answer('❌ Сначала необходимо зарегистрироваться. Используйте /start')
        return
    try:
        data = json.loads(message.web_app_data.data)
        response_text = (
            f'✅ Данные получены от {registered_users[user_id]["name"]}!\n\n'
            f'<b>{data.get("title", "Без названия")}</b>\n\n'
            f'<code>{data.get("desc", "Без описания")}</code>\n\n'
            f'{data.get("text", "Пустой текст")}'
        )
        await message.answer(response_text, parse_mode=ParseMode.HTML)
    except json.JSONDecodeError:
        await message.answer('❌ Ошибка при обработке данных. Неверный формат.')


@router.message(Command('profile'))
async def show_profile(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id in registered_users:
        user_data = registered_users[user_id]
        profile_text = (
            f'👤 <b>Ваш профиль:</b>\n\n'
            f'Имя: {user_data["name"]}\n'
            f'Телефон: {user_data["phone"]}\n'
            f'ID: {user_data["id"]}\n'
            f'Зарегистрирован: {datetime.fromisoformat(user_data["registration_date"]).strftime("%d.%m.%Y %H:%M")}'
        )
        await message.answer(profile_text, parse_mode=ParseMode.HTML)
    else:
        await message.answer('❌ Вы не зарегистрированы. Используйте /start для регистрации.')


@router.message(Command('contact'))
async def share_number(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id in registered_users:
        await message.answer(
            'Вы уже зарегистрированы. Хотите обновить контакт?',
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [KeyboardButton(text='📱 Обновить контакт', request_contact=True)],
                    [KeyboardButton(text='❌ Отмена')],
                ],
            ),
        )
    else:
        await send_welcome_message(message)


@router.message(F.text == '❌ Отмена')
async def cancel_action(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id in registered_users:
        await open_mini_app(message, user_id)
    else:
        await message.answer('Действие отменено. Используйте /start для начала.', reply_markup=ReplyKeyboardRemove())


@router.message()
async def fallback_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id in registered_users:
        await open_mini_app(message, user_id)
    else:
        await message.answer(
            '👋 Добро пожаловать!\n'
            'Для использования бота необходимо зарегистрироваться.\n\n'
            'Пожалуйста, используйте команду /start'
        )


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
