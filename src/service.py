import random
from functools import wraps

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.database import db_manager
from src.models import User, Hero


def edit_message(func):
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        # Вызываем функцию для получения нового текста и клавиатуры
        new_text, new_reply_markup = await func(callback, *args, **kwargs)

        if not new_reply_markup:
            new_reply_markup = InlineKeyboardMarkup(inline_keyboard=[])

        # Обновляем текст сообщения и клавиатуру
        await callback.message.edit_text(text=new_text, reply_markup=new_reply_markup)

        # Закрываем инлайн-уведомление
        await callback.answer()

    return wrapper


def derangement(lst):
    """Генерирует деренжмент списка."""
    while True:
        deranged = lst.copy()
        random.shuffle(deranged)
        if all(a.id != b.id for a, b in zip(lst, deranged)):
            return deranged


async def randomize_gifts():
    async with db_manager.session_maker() as session:
        # Получаем всех пользователей
        stmt = select(User)
        result = await session.execute(stmt)
        users: list[User] = result.scalars().all()

        if len(users) < 2:
            raise ValueError(
                "Необходимо как минимум два пользователя для организации Тайного Санты."
            )

        # Генерируем деренжмент
        deranged_users = derangement(users)

        # Назначаем gift_to_id для каждого пользователя
        for giver, receiver in zip(users, deranged_users):
            giver.gift_to_id = receiver.id

        try:
            await session.commit()
            print("Подарки успешно распределены!")
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при распределении подарков: {e}")
            raise


async def get_name_by_telegram_username(tg_username: str) -> str:
    async with db_manager.session_maker() as session:
        # Получаем всех пользователей
        stmt = select(User).where(User.tg_username == tg_username)
        result = await session.execute(stmt)
        user = result.scalars().one_or_none()
        if user is None:
            raise ValueError
        return user.name


async def get_id_by_telegram_username(tg_username: str) -> int:
    async with db_manager.session_maker() as session:
        # Получаем всех пользователей
        stmt = select(User).where(User.tg_username == tg_username)
        result = await session.execute(stmt)
        user = result.scalars().one_or_none()
        if user is None:
            raise ValueError
        return user.id


async def get_receiver_name(tg_username: str) -> str:
    async with db_manager.session_maker() as session:
        # Получаем всех пользователей
        stmt = select(User).where(User.tg_username == tg_username)
        result = await session.execute(stmt)
        user = result.scalars().one_or_none()
        if user is None:
            raise ValueError
        id_ = user.gift_to_id
        user = await session.get(User, id_)
        return user.name


async def get_hero(tg_username: str) -> str | None:
    async with db_manager.session_maker() as session:
        # Получаем всех пользователей
        stmt = (select(User)
                .options(selectinload(User.hero))
                .where(User.tg_username == tg_username))
        result = await session.execute(stmt)
        user = result.scalars().one_or_none()
        if user is None:
            raise ValueError
        if user.hero:
            return user.hero.name


async def get_free_heroes(tg_username: str) -> list[Hero]:
    async with db_manager.session_maker() as session:
        # Получаем tg_username пользователя, чтобы искать героев, которые не заняты
        stmt = select(User).filter(User.tg_username == tg_username)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if not user:
            return []  # Пользователь не найден

        # Получаем героев, которые не связаны с пользователем
        stmt = select(Hero).filter(Hero.user == None)  # Герой, который не связан с пользователем
        result = await session.execute(stmt)
        heroes = result.scalars().all()

        return heroes


def create_hero_inline_keyboard(heroes: list[Hero]) -> InlineKeyboardMarkup:
    # Группируем героев по 2
    hero_pairs = [heroes[i:i + 2] for i in range(0, len(heroes), 2)]

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=hero.name, callback_data=f"hero_{hero.id}")
                for hero in pair
            ]
            for pair in hero_pairs
        ]
    )

    return inline_keyboard


async def hero_is_free(hero_id: int) -> bool:
    async with db_manager.session_maker() as session:
        stmt = (select(Hero)
                .where(and_(Hero.id == hero_id, Hero.user == None))
                )
        result = await session.execute(stmt)
        hero = result.scalars().first()
        return bool(hero)


async def set_hero_to_user(tg_username: str, hero_id: int):
    async with db_manager.session_maker() as session:
        stmt = select(User).filter(User.tg_username == tg_username)
        result = await session.execute(stmt)
        user = result.scalars().first()

        user.hero_id = hero_id
        await session.commit()
