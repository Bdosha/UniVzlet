from aiogram import F
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, FSInputFile
from telethon.sync import TelegramClient

import asyncio
from datetime import datetime
import pytz

import structure
import get_data
import database
import config

bot = Bot(config.token)
dp = Dispatcher()

global_parameters = {'loop': False,
                     'ol': False,
                     'broadcast': False,
                     'cycle': 0}


def get_user_info(use):
    database.start_command(use.from_user.id)
    database.set_username(use.from_user.id, use.from_user.username)
    if type(use) is CallbackQuery:
        return use.from_user.username, use.from_user.id, use.data
    if type(use) is Message:
        return use.from_user.username, use.from_user.id, use.text


def zagl(string):
    return string[0].upper() + string[1:]


def set_program_text(program):
    return f'📍 Появилась {structure.set_title(program["title"])}\n\n' \
           f'{structure.icons[program["subject"]]} Предмет - {program["subject"]}\n' \
           f'🎒 Для {program["class"]} классов\n' \
           f'🗓️ С{program["dates"][1:]}\n' \
           f'{structure.place_icons[program["place"]][0]} Место - {structure.place_icons[program["place"]][1]}\n\n' \
           f'❗ Регистрация до {program["register"]}'


def set_olymp_text(olymp):
    title = list(olymp['dates'].keys())[0]
    date = olymp['dates'][title].lower()
    temp = "\n".join([zagl(i) for i in olymp["subjects"]])
    date = date.split()[-1]
    if len(date.split('.')[0]) == 1:
        date = '0' + date
    if not 'до' in date:
        date = 'до ' + date
    return f'📍 Совсем скоро начнется {olymp["title"]}\n\n' \
           f'👀 Дисциплины: {temp}\n' \
           f'🎒 Для {olymp["classes"][0]}-{olymp["classes"][-1]} классов\n' \
           f'🏅 Место РЦОИ - {olymp["place"]}\n' \
           f'📶 Уровень - {olymp["level"]}\n' \
           f'❗ {zagl(title)} {date}'


async def main_loop():
    print('Начало рассылки программ')

    hour = datetime.now(pytz.timezone('Europe/Moscow')).hour
    if hour > 20 or hour < 8:
        print('Плохое время')
        await asyncio.sleep(3600)
        await main_loop()

    users = database.send_program()
    get_data.parse()
    programs = get_data.programs()
    new = []
    for program in programs:
        if not program['place'] in structure.place_icons:
            program['place'] = "АНОО «Областная гимназия им. Е. М. Примакова»"
        classes = ([i for i in
                    range(int(program['class'].split('-')[0]), int(program['class'].split('-')[-1]) + 1)]
                   + [None, 0])

        for user in users[program['subject']]:

            if not database.get(user, 'class') in classes:
                continue
            try:
                await bot.send_photo(chat_id=user,
                                     photo=program['image'],
                                     caption=set_program_text(program),
                                     reply_markup=structure.set_url(program["url"]))
                print(f'[+] {program["title"]} отправлена в пользователю {user}')

                await asyncio.sleep(2.1)
            except:
                pass
        new.append(program['url'])
    database.new_urls(new)
    print('Рассылка программ завершена')
    print('Начало рассылки олимпиад')
    users = database.send_olymp()
    all_olymps = get_data.olymps()
    for olymp in all_olymps:
        for subject in olymp['subjects']:
            if not zagl(subject) in structure.subjects:
                continue
            for user in users[zagl(subject)]:
                if not database.get(user, 'class') in olymp['classes'] + [None, 0]:
                    continue
                try:
                    await bot.send_message(chat_id=user,
                                           text=set_olymp_text(olymp),
                                           reply_markup=structure.set_url(olymp["url"]))
                    print(f'[+] {olymp["title"]} отправлена в пользователю {user}')

                    await asyncio.sleep(2.1)
                except:
                    pass
    database.new_urls([i['url'] for i in all_olymps])
    print('Рассылка олимпиад завершена')
    await asyncio.sleep(21600)
    await main_loop()


async def start_bot():
    async with TelegramClient('data', config.api_id, config.api_hash,
                              device_model="",
                              system_version="",
                              app_version="",
                              lang_code="",
                              system_lang_code="") as client:
        await client.send_message('more_vzlet_bot', '/start')


@dp.message(Command('log'))
async def log(message: Message):
    if message.from_user.id in config.admins:
        try:
            await message.answer_document(FSInputFile(path='nohup.out'))
        except:
            await message.answer('Файл пустой')
        database.export_sheet()
        await message.answer_document(FSInputFile(path='data/Пользователи.xlsx'))
        await message.answer_document(FSInputFile(path='data/Ссылки.xlsx'))


@dp.message((F.text == '/start') & (F.from_user.username == ''))
async def start_command(message: Message):
    print(*get_user_info(message))
    if not global_parameters['loop']:
        await bot.send_message(chat_id=0, text='Бот запущен')
        global_parameters['loop'] = True
        await main_loop()
        return


@dp.message(CommandStart())
async def start_command(message: Message):
    print(*get_user_info(message))

    await message.answer(text=structure.text_start,
                         reply_markup=structure.main_menu)
    await asyncio.sleep(2)

    await message.answer(
        text=structure.text_start_2,
        reply_markup=structure.set_middle_but('main_menu', message.from_user.id))
    await asyncio.sleep(5)
    await message.answer(
        text=structure.text_start_3,
        reply_markup=structure.add_keys(message.from_user.id, True))


@dp.message(Command('broadcast'))
async def broadcast_command(message: Message):
    print(*get_user_info(message))
    if not message.from_user.id in config.admins:
        return
    await message.answer('Напиши сообщение')
    global_parameters['broadcast'] = True


@dp.message(lambda message: message.from_user.id in config.admins and global_parameters['broadcast'])
async def broadcast(message: Message):
    print(*get_user_info(message))
    global_parameters['broadcast'] = False
    await bot.copy_message(from_chat_id=message.from_user.id, chat_id=message.from_user.id,
                           message_id=message.message_id,
                           reply_markup=structure.confirm_broadcast)


@dp.callback_query(F.data == 'confirm')
async def cansel(callback: CallbackQuery):
    print(*get_user_info(callback))
    users = database.all_users()
    broadcast = database.new_broadcast()
    msg = await callback.message.answer("Рассылка начата")
    await callback.message.edit_reply_markup(None)
    for user in users:
        try:
            await bot.copy_message(from_chat_id=callback.from_user.id, chat_id=user,
                                   message_id=callback.message.message_id,
                                   reply_markup=structure.set_heart(broadcast, 0))
            print('Сообщение отправлено', user)
            await asyncio.sleep(2.1)
        except:
            pass
    await msg.edit_text('Рассылка завершена')


@dp.message(F.text == '🔔 Настройка уведомлений')
async def notification_settings(message: Message):
    print(*get_user_info(message))

    await message.answer(text=structure.text_settings,
                         reply_markup=structure.set_middle_but('main_menu', message.from_user.id),
                         parse_mode="HTML")


@dp.message(F.text == '🏅 Олимпиады')
async def get_olymps(message: Message):
    print(*get_user_info(message))
    if not message.from_user.id in global_parameters:
        global_parameters[message.from_user.id] = False

    if global_parameters[message.from_user.id]:
        await message.answer(text=structure.text_wait)
        return
    global_parameters[message.from_user.id] = True
    olymps = get_data.olymps(True)
    subjects = database.send_custom(message.from_user.id)
    temp = olymps.copy()
    olymps = []
    for olymp in temp:
        for subject in olymp['subjects']:
            if zagl(subject) in subjects:
                olymps.append(olymp)

    if not olymps:
        await message.answer('Похоже, что сейчас олимпиад нет')
        global_parameters[message.from_user.id] = False
        return
    await message.answer(text="Готовьтесь, возможно это надолго")
    await asyncio.sleep(1)
    await message.answer(text="Вот список всех олимпиад по вашим профилям на ближайшую неделю:",
                         reply_markup=structure.cansel,
                         parse_mode="HTML")

    subjects = database.send_custom(message.from_user.id)
    for olymp in olymps:
        if not global_parameters[message.from_user.id]:
            return

        for subject in olymp['subjects']:
            if zagl(subject) in subjects:
                await message.answer(text=set_olymp_text(olymp),
                                     reply_markup=structure.set_url(olymp["url"]))
                await asyncio.sleep(2.1)
                break
    global_parameters[message.from_user.id] = False
    await message.answer('Получилось найти что-то по душе?', reply_markup=structure.main_menu)


@dp.message(F.text == '❤️ Смены')
async def get_programs(message: Message):
    print(*get_user_info(message))

    if not message.from_user.id in global_parameters:
        global_parameters[message.from_user.id] = False

    if global_parameters[message.from_user.id]:
        await message.answer(text=structure.text_wait)
        global_parameters[message.from_user.id] = False
        return
    global_parameters[message.from_user.id] = True

    programs = get_data.programs(True)
    subjects = database.send_custom(message.from_user.id)
    programs = [program for program in programs if program['subject'] in subjects]
    if not programs:
        await message.answer('Похоже, что сейчас смен нет')
        global_parameters[message.from_user.id] = False

        return
    await message.answer(text="Вот список актуальных смен по вашим профилям:",
                         reply_markup=structure.cansel,
                         parse_mode="HTML")

    for program in programs:
        if not program['place'] in structure.place_icons:
            program['place'] = "АНОО «Областная гимназия им. Е. М. Примакова»"
        if not global_parameters[message.from_user.id]:
            return

        await message.answer_photo(photo=program['image'],
                                   caption=set_program_text(program),
                                   reply_markup=structure.set_url(program["url"]))
        await asyncio.sleep(2.1)
    global_parameters[message.from_user.id] = False
    await message.answer('Получилось найти что-то по душе?', reply_markup=structure.main_menu)


@dp.message(F.text == '❌ Отмена')
async def cansel(message: Message):
    print(*get_user_info(message))
    global_parameters[message.from_user.id] = False
    await message.answer('Отменено', reply_markup=structure.main_menu)


@dp.callback_query(F.data.in_(list(structure.graph.keys()) + structure.subjects))
async def navigation(callback: CallbackQuery):
    print(*get_user_info(callback))
    if callback.data in structure.subjects:
        reply = structure.set_notif(callback.from_user.id, callback.data)
    else:
        reply = structure.set_middle_but(callback.data, callback.from_user.id)

    await callback.message.edit_text(text='Навигация по категориям',
                                     reply_markup=reply)


@dp.callback_query(F.data == 'olymp')
async def olymp(callback: CallbackQuery):
    print(*get_user_info(callback))

    database.set_olymp(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=structure.add_keys(callback.from_user.id))


@dp.callback_query(F.data == 'more')
async def more(callback: CallbackQuery):
    print(*get_user_info(callback))

    await callback.message.edit_reply_markup(reply_markup=structure.add_keys(callback.from_user.id))


@dp.callback_query(F.data == 'klass')
async def set_klass(callback: CallbackQuery):
    print(*get_user_info(callback))

    user_id = callback.from_user.id
    if not database.get(user_id, 'class') in [0, None]:
        database.set_klass(user_id, 0)
        await callback.message.edit_reply_markup(reply_markup=structure.add_keys(user_id))
        return
    await callback.message.edit_reply_markup(reply_markup=structure.klass_but())


@dp.callback_query(F.data.in_(structure.klasses))
async def choose_class(callback: CallbackQuery):
    print(*get_user_info(callback))

    database.set_klass(callback.from_user.id, int(callback.data.replace('_klass', '')))
    await callback.message.edit_reply_markup(reply_markup=structure.add_keys(callback.from_user.id))


@dp.callback_query(F.data.in_(structure.hearts))
async def like(callback: CallbackQuery):
    try:
        heart = database.heart(callback.from_user.id, int(callback.data))
    except:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer('Пост был удален 💔', show_alert=True)
        return

    new = structure.set_heart(callback.data, heart[0])

    if new != callback.message.reply_markup:
        print(*get_user_info(callback))
        await callback.message.edit_reply_markup(reply_markup=new)
    if not heart[1]:
        await callback.answer('Можно поставить только одно ❤️', show_alert=True)


@dp.message(lambda message: message.from_user.id == message.chat.id)
async def message(message: Message):  #
    print(*get_user_info(message))

    await message.answer('Неизвестная команда')


if __name__ == '__main__':
    asyncio.run(start_bot())
    print('Бот запущен')
    dp.run_polling(bot)
