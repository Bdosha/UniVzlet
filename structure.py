from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import database

onoff = ['❌', '✅']


icons = {'Астрономия': '🔭', 'Математика': '📏', 'Русский язык': '🇷🇺', 'Обществознание': '👥', 'Литература': '📚',
         'Испанский язык': '🇪🇸', 'География': '🌍', 'Технология': '🛠️', 'История': '📜', 'Искусство (МХК)': '🏛️',
         'Экономика': '💹', 'Право': '⚖️', 'Биология': '🍃', 'Английский язык': '🇬🇧', 'Итальянский язык': '🇮🇹',
         'Китайский язык': '🇨🇳', 'Французский язык': '🇫🇷', 'Немецкий язык': '🇩🇪', 'Экология': '🌳', 'Химия': '🧪',
         'Информатика': '💻', 'Физическая культура': '🏀', 'Физика': '⚛️',

         'Проектная программа': '💘',

         'Акварельная живопись': '🖌️', 'Анималистическая скульптура': '🍯', 'Прикладное искусство': '🧑‍🎨',

         'Шахматы': '♟️',

         'Монументальная живопись': '🖼️', 'Архитектура': '🗿'
         }

subjects = list(icons.keys())

iss_keys = {'Основы многослойной акварельной живописи': 'Акварельная живопись',
            'Основы декоративно-прикладного искусства': 'Прикладное искусство',
            'Основы анималистической скульптуры': 'Анималистическая скульптура',
            'Монументальная и станковая живопись': 'Монументальная живопись'}

place_icons = {"АНОО «Физтех-лицей» им. П.Л. Капицы": ["💙", "Физтех-лицей"],
               "в дистанционном формате «Вебинар»": ["🤍", "Онлайн"],
               "АНОО «Областная гимназия им. Е. М. Примакова»": ["❤️", "Гимназия Примакова"],
               "ФГБОУ ВО «Академия акварели и изящных искусств Сергея Андрияки»": ["💚", "Академия Андрияки"],
               "ООО «СК Сатурн»": ["💜", "СК Сатурн"],
               'ФГБОУ ВО «Государственный университет просвещения»': ['🩵', 'ГУ Просвещения']}

title = {
    'Первая': "I",
    'Вторая': "II",
    'Третья': "III",
    'Четвертая': "IV",
    'Интенсивная профильная образовательная ': '',
    'интенсивная профильная образовательная ': '',
    'образовательная ': ''

}

mouth = {' января ': '.01.',
         ' февраля ': '.02.',
         ' марта ': '.03.',
         ' апреля ': '.04.',
         ' мая ': '.05.',
         ' июня ': '.06.',
         ' июля ': '.07.',
         ' августа ': '.08.',
         ' сентября ': '.09.',
         ' октября ': '.10.',
         ' ноября ': '.11.',
         ' декабря ': '.12.'}

graph = {'main_menu': ["🔬 Наука", "🎨 Искусство", "⚽ Спорт"],

         "🔬 Наука": ["🌐 Языки", "♾️ Технические науки", "🍁 Естественные науки", "👥 Гуманитарные науки", "👀 Прочее"],
         "🎨 Искусство": ['Акварельная живопись', 'Анималистическая скульптура', 'Прикладное искусство',
                         'Монументальная живопись', 'Архитектура'],
         "⚽ Спорт": ["Шахматы"],

         "🌐 Языки": ['Русский язык', 'Испанский язык', 'Английский язык',
                     'Итальянский язык', 'Китайский язык', 'Французский язык', 'Немецкий язык'],
         "♾️ Технические науки": ['Информатика', 'Математика', 'Технология'],
         "🍁 Естественные науки": ['Астрономия', 'Биология', "Экология", "Физика", "Химия"],
         "👥 Гуманитарные науки": ['Обществознание', 'География', 'История', 'Искусство (МХК)', 'Экономика', 'Право',
                                  'Литература'],
         "👀 Прочее": ["Проектная программа", 'Физическая культура']
         }

back_graph = {}
for key in graph:
    for sub in graph[key]:
        back_graph[sub] = key

get_olymps = KeyboardButton(text='🏅 Олимпиады')
get_programs = KeyboardButton(text='❤️ Смены')

settings = KeyboardButton(text='🔔 Настройка уведомлений')

main_menu = ReplyKeyboardMarkup(keyboard=[[get_olymps, get_programs], [settings]],
                                resize_keyboard=True)
additional = InlineKeyboardButton(
    text=f'✨ Дополнительные настройки',
    callback_data='more')

confirm_broadcast = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
    text=f'✅ Подтвердить',
    callback_data='confirm')]])

settings = KeyboardButton(text='🔔 Настройка уведомлений')

cansel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]],
                             resize_keyboard=True)


def set_title(data: str):
    for i in title.keys():
        data = data.replace(i, title[i])
    data = data.split('(')[0].replace('программа', 'смена')
    if data[0] != 'I':
        data = data[0].lower() + data[1:]
    return data


def set_url(url):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text='Перейти',
            url=url)]])


def set_back(now):
    return [InlineKeyboardButton(
        text='🚪 Назад',
        callback_data=back_graph[now])]


def set_heart(broadcast_id, now):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=f'❤️ - {now}',
            callback_data=broadcast_id)]])


def olymp_button(user_id):
    temp = database.get(user_id, 'olymp')
    if not temp:
        temp = 0
    return InlineKeyboardButton(
        text=f'{onoff[temp]} Уведомления об олимпиадах',
        callback_data='olymp')


def klass_but():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=f'{i} Класс',
        callback_data=f'{i}_klass')] for i in range(2, 12)])


def add_keys(user_id, flag=False):
    temp = database.get(user_id, 'olymp')
    if not temp:
        temp = 0
    olymp = InlineKeyboardButton(
        text=f'{onoff[temp]} Уведомления об олимпиадах',
        callback_data='olymp')
    temp = database.get(user_id, 'class')
    if not temp:
        temp = 0
    if temp == 0:
        klass = InlineKeyboardButton(
            text=f'❌ Фильтр по классу',
            callback_data='klass')
    else:
        klass = InlineKeyboardButton(
            text=f'✅ Фильтр по классу: {temp}',
            callback_data='klass')
    if flag:
        return InlineKeyboardMarkup(inline_keyboard=[[olymp], [klass]])

    return InlineKeyboardMarkup(inline_keyboard=[[olymp], [klass], set_back("🔬 Наука")])


def set_middle_but(now, user_id):
    if now == 'main_menu':
        but = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=i,
                callback_data=i)] for i in graph[now]])
        but.inline_keyboard.append([additional])
        return but
    if graph[now][0] in subjects:
        notifs = database.get_notif(user_id)
        but = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text=f'{icons[i]} {i} - {onoff[notifs[subjects.index(i)]]}',
                callback_data=i)] for i in graph[now]])
        but.inline_keyboard.append(set_back(now))
        return but
    but = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=i,
            callback_data=i)] for i in graph[now]])
    but.inline_keyboard.append(set_back(now))
    return but


def set_notif(user_id, subject):
    notifs = database.set_notif(user_id, subjects.index(subject))
    now = ''
    for i in graph:
        for j in graph[i]:
            if subject in j:
                now = i
                break

    but = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=f'{icons[i]} {i} - {onoff[notifs[subjects.index(i)]]}',
            callback_data=i)] for i in graph[now]])
    but.inline_keyboard.append(set_back(now))
    return but


klasses = [f'{i}_klass' for i in range(2, 12)]
hearts = [str(i) for i in range(1000)]

text_start = '👋 Привет, подмосковный олимпиадник!\n\n' \
             'ℹ️ Я бот, для отслеживания появления новых смен в ОЦ Взлёт начала олимпиад РЦОИ.\n'
text_start_2 = '⚙️ Давай включим нужные для тебя уведомления, ты сможешь изменить выбор в любой удобный момент!\n' \
               'Выбери интересующую категорию'
text_start_3 = '📍 В разделе дополнительных настроек можно включить уведомления об олимпиадах и указать свой класс, чтобы получать нужные оповещения'

text_settings = '⚙️ <b>Меню настроек</b>\n\n' \
                '✏️ Здесь вы можете выбрать нужные предметы\n\n' \
                'ℹ️ <i>В дополнительных настройках можно включить <b>оповещения о олимпиадах</b> и <b>фильтрацию по классу</b></i>'
text_wait = "⏳ Пожалуйста, дождитесь окончания другой рассылки смен или олимпиад"

if __name__ == "__main__":
    pass
