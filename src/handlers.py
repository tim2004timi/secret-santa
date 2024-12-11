import asyncio
import os

from aiogram import Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup,
)

from src.keyboards import menu_inline_keyboard
from src.service import (
    get_name_by_telegram_username,
    edit_message,
    get_id_by_telegram_username,
    get_receiver_name, get_hero, get_free_heroes, create_hero_inline_keyboard, hero_is_free, set_hero_to_user,
)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    try:
        name = await get_name_by_telegram_username(message.from_user.username)
    except ValueError:
        await message.answer(
            "Тебя почему-то нет в базе данных(\nНапиши об этом Тимохе!"
        )
        return
    answer = (
        f"🎅 Привет, мой дорогой <b>{name}</b>!\n\n"
        f"На носу уже <b>Новый Год</b>! Да-да осталось совсем ничего...\n"
        f"Настало время готовить подарочки ГейКлабу) 🎁\n"
        f"А также нужно приготовиться к ебануто-веселому косплею) 🎩"
    )
    await message.answer(answer)
    await asyncio.sleep(5)
    await menu(event=message)


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await menu(event=message)


@router.callback_query(F.data == "menu")
@edit_message
async def menu_callback(callback: CallbackQuery):
    await menu(event=callback)


@router.message(F.text == "📋 Меню")
async def menu_message(message: Message):
    await menu(event=message)


async def menu(event):
    tg_username = event.from_user.username
    if isinstance(event, CallbackQuery):
        await event.answer()

    try:
        name = await get_name_by_telegram_username(tg_username)
        id_ = await get_id_by_telegram_username(tg_username)
    except ValueError as e:
        print("Exc menu:", e)
        return

    answer = (
        f"Я вижу, ты в этом году очень жестко подкачался, хлопчик! 🎅\n\n"
        f"Поэтому ты в этом году заслуживаешь подарочка от Санты.\n"
        f"Но тебе надо обязательно что-то подарить своему кенту! 🎁\n\n"
        f"Великий и ужасный <b>{name}</b>, выбери кнопку!"
    )

    image_path = os.path.join("data", f"{id_}.png")

    if not os.path.isfile(image_path):
        await event.answer("Извините, изображение не найдено.")
        return

    photo = FSInputFile(image_path)

    if isinstance(event, CallbackQuery):
        await event.message.answer_photo(
            photo=photo, caption=answer, reply_markup=menu_inline_keyboard
        )
    elif isinstance(event, Message):
        await event.answer_photo(
            photo=photo, caption=answer, reply_markup=menu_inline_keyboard
        )


@router.callback_query(F.data == "gift")
async def gift_callback(callback: CallbackQuery):
    name = await get_receiver_name(callback.from_user.username)
    message = await callback.message.answer(
        f"🎯 Твоя цель: <u><b>{name}</b></u>\n\n"
        f"<i>Сообщение удалится через 5 сек</i>"
    )
    await callback.answer()
    await asyncio.sleep(5)
    await message.delete()


@router.callback_query(F.data == "cosplay-menu")
async def gift_callback(callback: CallbackQuery):
    try:
        name = await get_hero(callback.from_user.username)
    except ValueError:
        return
    await callback.answer()
    if name:
        message = await callback.message.answer(
            f"🎯 Твоя герой: <u><b>{name}</b></u>\n\n"
            f"<i>Сообщение удалится через 5 сек</i>"
        )
        await asyncio.sleep(5)
        await message.delete()
    else:
        heroes = await get_free_heroes(callback.from_user.username)
        inline_keyboard = create_hero_inline_keyboard(heroes)
        inline_keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="📋 Меню", callback_data=f"menu")]
        )
        answer = f"<b>Братишка, выбери героя для косплея!</b>\n\n" \
                 f"<i>Поспеши, а то кто-то может занять твоего героя</i>"
        await callback.message.answer(answer, reply_markup=inline_keyboard)


@router.callback_query(F.data.startswith("hero_"))
@edit_message
async def collection_detail_callback(
    callback: CallbackQuery,
) -> tuple[str, InlineKeyboardMarkup | None]:
    hero_id = int(callback.data.split("_")[1])

    if not await hero_is_free(hero_id):
        await callback.answer("Герой уже занят(")
        return

    await callback.answer()
    await set_hero_to_user(callback.from_user.username, hero_id)

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Меню", callback_data="menu"),
            ],
        ]
    )

    return "✅ Поздравляю, вы выбрали своего героя!", inline_keyboard


def register_handlers(dp: Dispatcher):
    dp.include_router(router)
