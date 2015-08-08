#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import sys

true_tests = [
    "ВЫШЛЮ ПЕРВАЯ ФОТОЧКУ.СЕЙЧАС ПИШИТЕ ТОЛЬКО СМС.ЯНА.095-24-25-705",
    "парень пригласит девушку в гости 050 93 59 529",
    "М  42.185.75.  Ищу женщ. для Всего! Днепродзержинск. 0639642652",
    "М ИЩУ Д/Ж 28-38 С ДНЕПРА ДЛЯ СЕР.ОТН 0989876082ММС",
    "Парень ищет Мужч.-Друга для общения и занятий! sms 096-601-36-99 Дн-жинск/Днепр",
    "М41Познакомится с девушкой для с/о и для интима.",
    "Парень25 скучает! Милые дев. кто порадует приятной смс ммс.050470216",
    "ПООБЩАЮСЬ С ДЕВУШКОЙ НА НЕСКРОМНЫЕ  ЛЮБЫЕ ТЕМЫ  063  182  10  88",
    "Симпат.парень на авто сделаю дев.нежный в обмен на ******Жду СмС СмС 097–356–71–6",
    "ПАРЕНЬ  36 Л. ПРИЕДУ К ДЕВУШКЕ ИЛИ ЗАБЕРУ К СЕБЕ (097) 3-100-333",
    "П 32 на авто встречусь с красивой д ж для и/о 050 22смс3 08 06",
    "ПРЕДЛОЖЕНИЕ НАПИСАТЬ СТИХИ АННУЛИРОВОНО 0 6 7  5 6 З  5 1 6 0",
    "НАПИШУ КРАСИВОЙ ЖЕНЩИНЕ СТИХИ О РАДОСТИ  О ГРУСТИ  О СМЕШНОМ. . . 0 6 7  5 6 З  5 1 6 0",
    "ЖДУ ЗВОНКА ОТ ЗАМУЖНЕЙ ДЕВУШКИ   ДЛЯ ТАЙНЫХ ВСТРЕЧ .  063 З17 0З 17",
    "М 42 ПОЗН С Ж ДЛЯ ДРУЖБЫ И ОБЩЕНИЯ СМС О СЕБЕ 067 860 ЗЗ 09",
    "ВЗРОСЛ   МУЖ  ПОЗНАК   С  ЖЕН.  БЕЗ  КОМПЛЕСОВ  0671З779ЗЗ",
    "взр.Ж.впечатлится интересным смс от умного высокого ПАРНЯ 06316З9З61"
]
"""
true_tests = [
              "ПАРНЯ 06316З9З61"
              ]
"""

# Empirical value
MAX_STEP_SIZE = 7

# Debug mode
DEBUG = 0

# Where store parsed results with phone numbers
file_phones = "phones.txt"

# Where store parsed results without phone numbers
file_no_phones = "no_phones.txt"


def process(test):
    parts = test.split(',')
    if len(parts)>1:

        # Omit digits in unicode format
        str = unicode(parts[1].decode("utf8")).replace(u'\u0417', "3")
        
        if DEBUG:
            print str, type(str), list(str)
        
        # Leave only numbers in string
        str = re.sub("[^0-9]", " ", str)

        if DEBUG:
            print str

        i = 0
        phone = ""
        phones = []
        for c in str:
            if c.isdigit():
                if i<MAX_STEP_SIZE:
                    i = 0
                    phone = phone + c
                elif len(phone):
                    phones.append(phone)
                    phone = c
                    i = 0
            elif len(phone):
                i = i+1

        if DEBUG:
            print "A: ", phone, phones
        if len(phone):
            phones.append(phone)
        phones = [phone for phone in phones if len(phone)>8]

        if not DEBUG:
            if len(phones):
                open(file_phones,"a").write(parts[0]+','+parts[1])
            else:
                open(file_no_phones,"a").write(parts[0]+','+parts[1])

        if DEBUG:
            print test, phones

if __name__ == "__main__":
    if not DEBUG:
        for line in sys.stdin:
            process(line)
    else:
        for line in true_tests:
            process(","+line)
