import requests
from bs4 import BeautifulSoup

from datetime import datetime
import pytz

import database
import structure


def olymps(custom=False):
    tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(tz).date()
    data = database.getData('data/actual.json')['olymps']
    actual_olymps = []
    for olymp in data:
        olymp_dates = data[olymp]['dates']
        title = list(olymp_dates.keys())[0]
        date = olymp_dates[title]
        if 'До' in date:
            date = date[3:]
        date = datetime.strptime(date, '%d.%m.%Y').date()
        if not (0 < (date - moscow_time).days < 7):
            continue
        actual_olymps.append(data[olymp])
    if custom:
        return actual_olymps
    return [i for i in actual_olymps if not i['url'] in database.get_urls()]


def programs(custom=False):
    tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(tz).date()
    data = database.getData('data/actual.json')['programs']
    actual_programs = []
    for program in data:
        date = data[program]['register'].split()[1]
        date = datetime.strptime(date, '%d.%m.%Y').date()
        if not (0 < (date - moscow_time).days):
            continue
        actual_programs.append(data[program])
    if custom:
        return actual_programs
    return [i for i in actual_programs if not i['url'] in database.get_urls()]


def get_programs(url):
    response_text = requests.get(url).text
    soup = BeautifulSoup(response_text, "html.parser")
    print(f'[+] Выполняю {url} : ', end='')
    all_html = [i for i in soup.findAll('article', {'class': 'post-news'}) if 'закрыта' not in str(i)]
    print('Выполнено')
    return [(i.find('a')['href'],
             i.find('div', {'class': 'offset-top-20'}).text.split('b>')[-1].replace('\n', '').replace('Предмет: ', ''),
             i.find('img')['src'].replace(' ', '').replace('\n', ''),
             i.find('div', {'class': 'offset-top-10'}).text.replace('\nКлассы: ', '')[:-1]) for i
            in all_html]


def get_info(data):
    url, subject, image, klass = data
    if subject in structure.iss_keys:
        subject = structure.iss_keys[subject]
    response_text = requests.get(url).text
    soup = BeautifulSoup(response_text, "html.parser")
    if not 'программа' in str(soup):
        return []
    print(f'[+] Выполняю {url} : ', end='')
    register = soup.find('div', {'id': 'tabs-n-1'}).findAll('p')[-1].find('b').text[3:].split()
    temp_reg = register[1]
    if len(temp_reg) == 1:
        temp_reg = '0' + temp_reg
    register = register[0] + ' ' + temp_reg + structure.mouth[f' {register[2]} '] + register[3]
    temp = {'url': url,
            'subject': subject,
            'title': soup.find('div', {'class': 'container'}).find('h3').text.replace('\n', ''),
            'class': klass,
            'dates': soup.find('div', {'id': 'tabs-n-1'}).find('p').find('strong').text,
            'register': register,
            'image': image}
    try:
        temp['place'] = soup.find('div', {'id': 'tabs-n-1'}).find('p').findAll('b')[-1].text
    except:
        try:
            temp['place'] = soup.find('div', {'id': 'tabs-n-1'}).find('p').findAll('strong')[1].text
        except:
            temp['place'] = soup.find('div', {'id': 'tabs-n-1'}).find('p').findAll('strong')[0].text.split('на базе ')[
                -1]

    # print(temp['register'])
    print('Готово')
    return temp


def parse():
    programs = []
    info = []
    sent = database.get_urls()
    new = []
    main_urls = ['https://reg.olympmo.ru/direction/science?page=1',
                 'https://reg.olympmo.ru/direction/science?page=2',
                 'https://reg.olympmo.ru/direction/science?page=3',
                 'https://reg.olympmo.ru/direction/art?page=1',
                 'https://reg.olympmo.ru/direction/art?page=2',
                 'https://reg.olympmo.ru/direction/art?page=3',
                 'https://reg.olympmo.ru/direction/sport?page=1',
                 'https://reg.olympmo.ru/direction/sport?page=2',
                 'https://reg.olympmo.ru/direction/sport?page=3',
                 'https://reg.olympmo.ru/direction/regular-classes']
    print('--Начало выполнения--')
    print('Получение всех программ')

    for url in main_urls:
        temp = get_programs(url)
        programs += [i for i in temp if not i[0] in sent]
        new += [i[0] for i in temp if not i[0] in sent]
    if programs:
        print('Получение информации о программах')
    for data in programs:
        temp = get_info(data)
        if temp:
            info.append(temp)
    # database.new_urls(new)

    temp = info
    info = {}

    for i in temp:
        info[i['url']] = i
    info.update(database.getData('data/actual.json')['programs'])
    database.addData('data/actual.json', 'programs', info)
    return info


if __name__ == "__main__":
    print(programs())
    pass  # for i in programs():
#     print(f"'{i['register']}',")
