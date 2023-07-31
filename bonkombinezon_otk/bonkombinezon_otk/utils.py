from datetime import date
from calendar import monthrange


class CustomStr:
    def __str__(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self, 'name'):
            return self.name
        elif hasattr(self, 'employee') and hasattr(self, 'product'):
            return f'{self.employee} {self.product}'
        else:
            return self.id


def safe_get(Model, **kwargs):
    try:
        return Model.objects.get(**kwargs)
    except Model.MultipleObjectsReturned:
        return Model.objects.filter(**kwargs).last()
    except Model.DoesNotExist:
        return None


def default_schedule(year=date.today().year):
    results = {
        year: {i: {} for i in range(1, 13)},
        year + 1: {i: {} for i in range(1, 13)}
    }
    for year, months in results.items():
        for month in months:
            days = monthrange(year, month)
            for day in range(1, days[1] + 1):
                if date(year, month, day).weekday() not in [5, 6]:
                    results[year][month][day] = 'Р'
                else:
                    results[year][month][day] = 'В'
    return results


months = {
    1: 'январь',
    2: 'февраль',
    3: 'март',
    4: 'апрель',
    5: 'май',
    6: 'июнь',
    7: 'июль',
    8: 'август',
    9: 'сентябрь',
    10: 'октябрь',
    11: 'ноябрь',
    12: 'декабрь',
}


if __name__ == '__main__':
    default_schedule(2023)