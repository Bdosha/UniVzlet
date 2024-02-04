import json
import sqlite3
import structure
import pandas as pd

con = sqlite3.connect('data/database.db')
cursor = con.cursor()


def addData(file_path, key, value):
    with open(file_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)

    data[key] = value

    with open(file_path, 'w', encoding='utf-8-sig') as json_file:
        json.dump(data, json_file, indent=8, ensure_ascii=False)


def getData(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)

    return data


def get(user_id, part):
    return cursor.execute(f"SELECT {part} FROM user_info WHERE user_id = {user_id}").fetchall()[0][0]


def set_olymp(user_id):
    temp = get(user_id, 'olymp')
    if not temp:
        temp = 0
    temp = abs(temp - 1)
    cursor.execute(f'UPDATE user_info SET olymp = {temp} WHERE user_id = {user_id}')
    con.commit()
    return temp


def get_notif(user_id):
    return [int(i) for i in
            cursor.execute(f'SELECT subjects FROM user_info WHERE user_id = {user_id}').fetchall()[0][0]]


def start_command(user_id):
    if not (user_id,) in cursor.execute('SELECT user_id FROM user_info').fetchall():
        cursor.execute(f"INSERT INTO 'user_info'(user_id, subjects) VALUES('{user_id}', '{'0' * 30}')")
        con.commit()


def set_notif(user_id, subject):
    now = get_notif(user_id)
    now[subject] = abs(now[subject] - 1)

    cursor.execute(f'UPDATE user_info SET subjects = "{"".join(list(map(str, now)))}" WHERE user_id = {user_id}')
    con.commit()
    return now


def get_urls():
    return [i[0] for i in cursor.execute('SELECT url FROM sent').fetchall()]


def new_urls(urls):
    for url in urls:
        cursor.execute(f"INSERT INTO 'sent'(url) VALUES('{url}')")
    con.commit()


def send_program():
    result = {i: [] for i in structure.subjects}
    for subject in range(len(structure.subjects)):
        for i in cursor.execute('SELECT * FROM user_info').fetchall():
            if i[3][subject] == '1':
                result[structure.subjects[subject]].append(i[0])
    return result


def send_olymp():
    result = {i: [] for i in structure.subjects}
    for subject in range(len(structure.subjects)):
        for i in cursor.execute('SELECT * FROM user_info').fetchall():
            if i[3][subject] == '1' and i[-1] == 1:
                result[structure.subjects[subject]].append(i[0])
    return result


def send_custom(user_id):
    result = []
    user = cursor.execute(f'SELECT subjects FROM user_info WHERE user_id = {user_id}').fetchall()[0][0]
    print(user)
    for i in range(len(structure.subjects)):
        if user[i] == '1':
            result.append(structure.subjects[i])

    return result


def all_users():
    return [i[0] for i in cursor.execute(f'SELECT user_id FROM user_info').fetchall()]


def new_broadcast():
    last = cursor.execute(f'SELECT id FROM broadcast').fetchall()[-1][0] + 1
    cursor.execute(f"INSERT INTO 'broadcast'(id) VALUES({last})")
    cursor.execute(f"CREATE TABLE '{last}'(user_id INT)")
    con.commit()

    return last


def heart(user_id, broad_id):
    last = [i[0] for i in cursor.execute(f'SELECT user_id FROM "{broad_id}"').fetchall()]
    if user_id in last:
        return len(last), False

    cursor.execute(f"INSERT INTO '{broad_id}'(user_id) VALUES({user_id})")
    cursor.execute(f'UPDATE broadcast SET hearts = {len(last) + 1} WHERE id = {broad_id}')
    con.commit()
    return len(last) + 1, True


def set_username(user_id, username):
    cursor.execute(f'UPDATE user_info SET username = "{username}" WHERE user_id = {user_id}')
    con.commit()


def set_klass(user_id, klass):
    cursor.execute(f'UPDATE user_info SET class = {klass} WHERE user_id = {user_id}')
    con.commit()


def export_sheet():
    df = pd.read_sql_query("SELECT * FROM user_info", sqlite3.connect('data/database.db'))
    df.to_excel('data/Пользователи.xlsx')
    df = pd.read_sql_query("SELECT * FROM sent", sqlite3.connect('data/database.db'))
    df.to_excel('data/Ссылки.xlsx')


if __name__ == '__main__':
    pass

