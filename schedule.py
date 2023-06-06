import pprint

import requests as rq
import json

days = [
    'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'
]

groups = {
    0: 'ОБЩ',
    1: '1ПГ',
    2: '2ПГ'
}


def get_schedule():
    week: int
    schedule: dict
    try:
        week = int(rq.get('https://iis.bsuir.by/api/v1/schedule/current-week').text) + 1
    except Exception as e:
        print("FUNC: get_schedule ERR:", e)
        return {}
    try:
        schedule = json.loads(rq.get('https://iis.bsuir.by/api/v1/schedule?studentGroup=150503').text)['schedules']
    except Exception as e:
        print("FUNC: get_schedule ERR:", e)
        return {}
    out = {}
    for day in days:
        for subject in schedule[day]:
            if week in subject['weekNumber'] and subject['lessonTypeAbbrev'] == 'ЛР':
                if not out.get(day):
                    out[day] = {}
                    out[day]['subject'] = []
                out[day]['subject'].append(f"{subject['subject']} {groups[subject['numSubgroup']]}")
    return out


if __name__ == "__main__":
    pprint.pprint(get_schedule())
