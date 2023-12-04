import re
from datetime import datetime, timedelta, date, time
from django.utils.datetime_safe import datetime as django_datetime

DATETIME_ZERO = datetime(1900, 1, 1, 0, 0, 0)
DATETIME_EPS = 60


# ===========================================================
#                Операции с датой и временем
# ===========================================================

def datetime_now() -> datetime:
    return django_datetime.now()


def add_datetime(dt: datetime, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> datetime:
    return dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def time_to_seconds(tm: time) -> float:
    return tm.hour * 3600 + tm.minute * 60 + tm.second + float(tm.microsecond) / 1e6


def seconds_to_time(seconds: float) -> time:
    return time(int(seconds / 3600), int(seconds / 60), int(seconds), int(seconds * 1e6))


# ===========================================================
#                     Конвертация в строку
# ===========================================================

def datetime_to_string(
        dt: datetime,
        is_full: bool = True,
        accuracy: int = 0,
        sep_date: str = '-',
        reverse_date: bool = False
) -> str:
    return date_to_string(dt.date(), sep=sep_date, reverse=reverse_date) + ' ' + \
           time_to_string(dt.time(), is_full=is_full, accuracy=accuracy)


def datetime_to_string_words(
        dt: datetime,
        is_full: bool = True,
        accuracy: int = 0,
        show_day_week: bool = False
) -> str:
    return date_to_string_words(dt.date(), show_day_week=show_day_week) + ' в ' + \
           time_to_string(dt.time(), is_full=is_full, accuracy=accuracy)


def datetime_to_string_relative(
    dt_now: datetime,
    dt_target: datetime,
    show_day_week: bool = False
) -> str:
    seconds = abs((dt_target - dt_now).seconds)
    if seconds < DATETIME_EPS:
        return 'сейчас'
    elif seconds < 60:
        return str(seconds) + 'сек.'
    elif seconds < 3600:
        return str(seconds / 60) + 'мин.'
    elif seconds < 86400:
        return str(seconds / 3600) + 'час.'

    days = (dt_target.date() - dt_now.date()).days
    if days == 1:
        return 'завтра в' + time_to_string(dt_target.time(), is_full=False)
    elif days == -1:
        return 'вчера в' + time_to_string(dt_target.time(), is_full=False)
    else:
        return date_to_string_words(dt_target,
                                    show_day_week=show_day_week,
                                    show_year=(dt_target.year != dt_now.year)) + \
               time_to_string(dt_target.time(), is_full=False)


def date_to_string(dt: date, sep: str = '-', reverse: bool = False) -> str:
    if reverse:
        return '{:02}'.format(dt.day) + sep + '{:02}'.format(dt.month) + sep + '{:04}'.format(dt.year)
    else:
        return '{:04}'.format(dt.year) + sep + '{:02}'.format(dt.month) + sep + '{:02}'.format(dt.day)


def date_to_string_words(dt: date, show_day_week: bool = False, show_year: bool = True) -> str:
    return str(dt.day) + ' ' + \
           month_to_string(dt.month) + '.' + \
           (' ' + str(dt.year) + ' года' if show_year else '') + \
           (' (' + day_week_to_string(dt.weekday()) + ')' if show_day_week else '')


def date_to_string_relative(
        dt_now: date,
        dt_target: date,
        show_day_week: bool = False
) -> str:
    days = (dt_target - dt_now).days

    if days == 0:
        return 'сегодня'
    elif days == 1:
        return 'завтра'
    elif days == -1:
        return 'вчера'
    else:
        return date_to_string_words(dt_target,
                                    show_day_week=show_day_week,
                                    show_year=(dt_target.year != dt_now.year))


def month_to_string(month_number: int) -> str:
    if month_number == 1:
        return 'янв'
    elif month_number == 2:
        return 'фев'
    elif month_number == 3:
        return 'мар'
    elif month_number == 4:
        return 'апр'
    elif month_number == 5:
        return 'май'
    elif month_number == 6:
        return 'июн'
    elif month_number == 7:
        return 'июл'
    elif month_number == 8:
        return 'авг'
    elif month_number == 9:
        return 'сен'
    elif month_number == 10:
        return 'окт'
    elif month_number == 11:
        return 'ноя'
    elif month_number == 12:
        return 'дек'
    else:
        return '?'


def day_week_to_string(month_number: int) -> str:
    if month_number == 0:
        return 'понедельник'
    elif month_number == 1:
        return 'вторник'
    elif month_number == 2:
        return 'среда'
    elif month_number == 3:
        return 'четверг'
    elif month_number == 4:
        return 'пятница'
    elif month_number == 5:
        return 'суббота'
    elif month_number == 6:
        return 'воскресенье'
    else:
        return '?'


def time_to_string(
        tm: time,
        is_full: bool = True,
        accuracy: int = 0
) -> str:
    if is_full:
        if accuracy > 0:
            format_ = '{:0' + str(accuracy) + '}'
            return '{:02}'.format(tm.hour) + ':' + \
                   '{:02}'.format(tm.minute) + ':' + \
                   '{:02}'.format(tm.second) + '.' + \
                   format_.format(tm.microsecond)
        else:
            return '{:02}'.format(tm.hour) + ':' + \
                   '{:02}'.format(tm.minute) + ':' + \
                   '{:02}'.format(tm.second)
    else:
        return '{:02}'.format(tm.hour) + ':' + \
               '{:02}'.format(tm.minute)


def time_to_string_relative(tm_now: time, tm_target: time) -> str:
    seconds = abs(time_to_seconds(tm_target) - time_to_seconds(tm_now))

    if seconds < DATETIME_EPS:
        return 'сейчас'
    if seconds < 60:
        return str(seconds) + 'сек.'
    elif seconds < 3600:
        return str(seconds / 60) + 'мин.'
    else:
        return str(seconds / 3600) + 'час.'


# ===========================================================
#                Конвертация строки в объект
# ===========================================================

def string_to_datetime(dt_string: str) -> datetime | None:
    if len(dt_string) >= 20:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}', dt_string):
            return None
    elif not re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', dt_string):
        return None

    year = int(dt_string[0:4])
    month = int(dt_string[5:7])
    day = int(dt_string[8:10])
    hour = int(dt_string[11:13])
    minute = int(dt_string[14:16])
    second = int(dt_string[17:19])

    if len(dt_string) >= 20:
        millisecond = int(dt_string[20:26])
    else:
        millisecond = 0

    return datetime(year, month, day, hour, minute, second, millisecond)


def string_to_date(dt_string: str, sep: str = '-', reverse: bool = False) -> date | None:
    if reverse:
        pattern = r'\d{2}' + sep + r'\d{2}' + sep + r'\d{4}'
        if not re.fullmatch(pattern, dt_string):
            return None

        day = int(dt_string[0:2])
        month = int(dt_string[3:5])
        year = int(dt_string[6:10])

    else:
        pattern = r'\d{4}' + sep + r'\d{2}' + sep + r'\d{2}'
        if not re.fullmatch(pattern, dt_string):
            return None

        year = int(dt_string[0:4])
        month = int(dt_string[5:7])
        day = int(dt_string[8:10])

    try:
        return date(year, month, day)
    except:
        return None


def string_to_time(tm_string: str) -> time | None:
    if len(tm_string) <= 8:
        if not re.fullmatch(r'\d{2}:\d{2}:\d{2}', tm_string):
            return None
    elif not re.fullmatch(r'\d{2}:\d{2}:\d{2}.\d{6}', tm_string):
        return None

    hour = int(tm_string[0:2])
    minute = int(tm_string[3:5])
    second = int(tm_string[6:8])

    if len(tm_string) >= 8:
        millisecond = int(tm_string[9:15])
    else:
        millisecond = 0

    return time(hour, minute, second, millisecond)
