#!/usr/bin/env python3

import sys
import time
import os
import csv
from subprocess import check_output, CalledProcessError
from functools import lru_cache


# Задаем константы для имени файла с треком,
# почасового рейта и валюту расчета.
FILE_NAME = 'timetracking.csv'
HOUR_RATE = 1000
CURRENCY = 'RUB'


def main():
    # Проверяем сперва в репозитории ли мы у Гита.
    # Если да - получаем путь к корневой папке репозитория.
    try:
        rootDir = getGitRoot()
        filename = os.path.join(rootDir, FILE_NAME)
    except OSError as err:
        # Если это не гит-репозиторий, то выходим нафиг.
        message = "OS error: {0}".format(err)
        sys.exit(message)

    # Если первым аргументом скрипта '-s', то возвращаем статистику
    # по отработанному и выходим.
    try:
        if sys.argv[1] == '-s':
            return getStats(filename)
    except IndexError:
        pass

    # Получаем колл-во отработанных минут
    # и дату/время начала текуцего рабочего периода.
    offset = getOffset()
    startDateTime = time.localtime(time.time() - (offset * 60))

    # Подготавливаем данные для записи в файл.
    logDate = time.strftime('%d %b %Y', startDateTime)
    logStartTime = time.strftime('%H:%M', startDateTime)
    logEndTime = time.strftime('%H:%M', time.localtime())
    # Комментарий к записи о проделанной работе.
    # Если не введен аргументом - пишем дефолтный.
    logComment = 'См. коммит.' if len(sys.argv) < 3 \
        else '"' + ' '.join(sys.argv[2:]) + '"'
    logHours = '%.1f' % (offset / 60)

    data = [logDate, logStartTime, logEndTime, logComment, logHours]
    new = os.path.isfile(filename)

    with open(filename, 'a+') as f:
        if not new:
            f.write('Date,Start,End,Comment,Hour(s)\n')
        f.write(','.join(data) + '\n')


def getOffset():
    '''
    Валидируем введенное значение отработанных минут.
    Если не введены - просим предоставить.
    '''
    try:
        minutes = sys.argv[1]
        if not minutes.isdigit():
            raise IndexError
        else:
            minutes = int(minutes)
    except IndexError:
        while True:
            try:
                minutes = int(
                    input("Нужно задать количество отработанных минут: "))
                break
            except ValueError:
                print("Оп-п-па! Введена ни разу не цифра. Пробуем заново...")

    return minutes


# Проверяем, что мы внутри гит-репозитррия,
# и если да, то вычисляем и отдаем путь к корневой дирректории репоозитория.
# С кэшем (ltu_cache) отработать должно быстрее.
@lru_cache(maxsize=1)
def getGitRoot():
    ''' Возвращаем абсолютный путь к корневой дирректории гит-репозитория '''
    try:
        base = check_output('git rev-parse --show-toplevel', shell=True)
    except CalledProcessError:
        raise IOError(
            'Текущая дирректория не является гит-репозиторием!\nДосвидания.')
    return base.decode('utf-8').strip()


def getStats(filename, col_index=4):
    '''
    Получаем статистику по затраченому времени и 
    заработанному лаве.
    '''
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            headerline = next(reader)
            hours = 0
            for row in reader:
                hours += float(row[col_index])
            sum = hours * HOUR_RATE
            # "Копейки" не учитываем.
            print('Затрачено {} часов | Заработано {} {}'.format(
                round(hours, 2), int(sum), CURRENCY))
    except FileNotFoundError:
        sys.exit('Файл с треком не найден!')


if __name__ == '__main__':
    main()
