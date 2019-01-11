import requests
from telebot import *
import config
from bs4 import BeautifulSoup
import time
import datetime
import traceback
from typing import Any

bot = TeleBot(config.access_token, threaded=False)
weekdays = ['/monday', '/tuesday', '/wednesday', '/thursday', '/friday', '/saturday', '/sunday']
weekdays_rus = ['понедельник', 'вторник', 'средy', 'четверг', 'пятницy', 'субботy', 'воскресенье']
weeknumber = ['четную', 'нечетную']


def get_page(group:str='K3140', week:str='') -> str:
    if week:
        week = str(week) + '/'
    url = '{domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(
        domain=config.domain,
        week=week,
        group=group)
    response = requests.get(url)
    web_page = response.text
    return web_page


def parse_for_schedule(web_page:str, day:str) -> Any:
    soup = BeautifulSoup(web_page, "html5lib")
    # Получаем таблицу с расписанием
    if day in weekdays:
        daynumber = str(weekdays.index(day) + 1) + 'day'
        schedule_table = soup.find("table", attrs={"id": daynumber})
    if not schedule_table:
        return
    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.text.replace('\n', '').replace('\t', '') for room in locations_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.replace('\n', '').replace('\t', '') for lesson in lessons_list]

    return times_list, locations_list, lessons_list


@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'])
def get_schedule(message) -> None:
    """ Получить расписание на указанный день """
    try:
        a = message.text.split()
    except ValueError:
        return None

    if len(a) > 1:
        try:
            day, group, week = a
        except ValueError:
            day, group = a
            week = ''
    else:
        day = a[0]
        group = 'K3140'
        week = ''
    if week in ' 12':
        pass
    else:
        bot.send_message(message.chat.id, "четность недели 1 или 2, введена другая")
    print(message.text, group)
    web_page = get_page(group, week)
    day_r = weekdays_rus[weekdays.index(day)]
    try:
        times_lst, locations_lst, lessons_lst = \
            parse_for_schedule(web_page, day)
    except TypeError:
        bot.send_message(message.chat.id, "данные введены неверно или нет пар")
        return None
    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}\n --- {}\n'.format(time, location, lession)
    if week == '1':
        bot.send_message(message.chat.id, 'расписание на {} для группы {}, на {} неделю'.format(day_r, group, weeknumber[0]), parse_mode='HTML')
    elif week == '2':
        bot.send_message(message.chat.id, 'расписание на {} для группы {}, на {} неделю'.format(day_r, group, weeknumber[1]), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'расписание на {} для группы {}, на все недели'.format(day_r, group), parse_mode='HTML')

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['near'])
def get_near_lesson(message):
    try:
        a = message.text.split()
    except ValueError:
        return None

    if len(a) > 1:
        group = a[1]
    else:
        group = 'K3140'

    if int(datetime.datetime.today().strftime('%U')) % 2 == 1:
        week = 1
    else:
        week = 2
    print(message.text, group)
    now = (datetime.datetime.now().strftime('%H:%M'))
    day = datetime.datetime.now()
    day = weekdays[day.weekday()]
    web_page = get_page(group, str(week))
    n = 0
    day_r = weekdays_rus[weekdays.index(day)]
    days = day
    for i in range(7):
        a = parse_for_schedule(web_page, day)
        if a:
            n += 1
            if n == 2:
                break
            b = a
            day1 = day
            day = weekdays.index(day) + 1
            if day == 7:
                day -= 7
                day = weekdays[day]
            else:
                day = weekdays[day]
        else:
            day = weekdays.index(day) + 1
            if day == 7:
                day -= 7
                day = weekdays[day]
            else:
                day = weekdays[day]
    if n == 0:
        bot.send_message(message.chat.id, "данные введены неверно", parse_mode='HTML')
        return None
    times_lst, locations_lst, lessons_lst = b
    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        if day1 != days:
            resp = '<b>{}</b>, {}\n --- {}\n'.format(time, location, lession)
            day_r = weekdays_rus[weekdays.index(day1)]
            break
        elif now < time[0:5]:
            resp = '<b>{}</b>, {}\n --- {}\n'.format(time, location, lession)
            day_r = weekdays_rus[weekdays.index(day1)]
            break
        elif time[0:5] < now < time[6:11]:
            pass
        elif now > time[6:11]:
            times_lst, locations_lst, lessons_lst = a
            for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
                resp = '<b>{}</b>, {}\n --- {}\n'.format(time, location, lession)
                day_r = weekdays_rus[weekdays.index(day)]
                break
    bot.send_message(message.chat.id, 'ближайшая пара для группы {} в {}'.format(group, day_r), parse_mode='HTML')
    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['tomorrow'])
def get_tommorow(message):
    """ Получить расписание на следующий день """
    try:
        day, group = message.text.split()
    except ValueError:
        group = 'K3140'
    if int(datetime.datetime.today().strftime('%U')) % 2 == 1:
        week = 1
    else:
        week = 2
    print(message.text, group)
    today = datetime.datetime.now() + datetime.timedelta(days=1)
    tomorrow = today
    if today.weekday() == 7:
        tomorrow = today + datetime.timedelta(days=1)
    tomorrow = weekdays[tomorrow.weekday()]
    web_page = get_page(group, str(week))
    day_r = weekdays_rus[weekdays.index(tomorrow)]
    try:
        times_lst, locations_lst, lessons_lst = \
            parse_for_schedule(web_page, tomorrow)
    except TypeError:
        bot.send_message(message.chat.id, "данные введены неверно или нет пар")
        return None
    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}\n --- {}\n'.format(time, location, lession)
    bot.send_message(message.chat.id, 'расписание на завтра ({}) для группы {}'.format(day_r, group), parse_mode='HTML')
    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
    """ Получить расписание на всю неделю для указанной группы """
    try:
        a = message.text.split()
    except ValueError:
        return None

    if len(a) > 1:
        try:
            _, group, week = a
        except ValueError:
            _, group = a
            week = ''
    else:
        group = 'K3140'
        week = ''
    if week in ' 12':
        pass
    else:
        bot.send_message(message.chat.id, "четность недели 1 или 2, введена другая")
    print(message.text, group)
    web_page = get_page(group, str(week))
    bot.send_message(message.chat.id, 'расписание на {} неделю для группы {}'.format(week, group), parse_mode='HTML')
    n = 0
    for day in weekdays:
        day_r = weekdays_rus[weekdays.index(day)]
        a = parse_for_schedule(web_page, day)
        if a:
            resp = ''
            times_lst, locations_lst, lessons_lst = a
            for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
                resp += '<b>{}</b>, {}\n --- {}\n'.format(time, location, lession)
            bot.send_message(message.chat.id, 'расписание на {}\n {}'.format(day_r, resp), parse_mode='HTML')
            n += 1
    if n == 0:
        bot.send_message(message.chat.id, "данные введены неверно", parse_mode='HTML')
        return None

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Ассалам алейкумы")
        
@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, "/start для выхода в меню \n /tomorrow для просмотра расписания на завтра \n /all для просотра расписания на всю неделю \n /near для простотра ближайшей пары")

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)

    except:
        traceback.print_exc()
        time.sleep(15)
