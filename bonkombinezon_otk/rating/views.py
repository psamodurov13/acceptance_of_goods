from datetime import datetime, timedelta
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from otk.models import Employees
from .models import *
from bonkombinezon_otk.settings import logger


def rating_page(request):
    weeks = TimePeriod.objects.get(id=1).period
    time_now = datetime.now()
    before_time = time_now - timedelta(days=weeks * 7)
    employees = Employees.objects.filter(status=True)
    rating_ranges = RatingRange.objects.all()
    days = weeks * 5
    results = []
    for emp in employees:
        result = {
            'name': emp.name,
        }
        schedule = emp.schedule
        logger.info(f'BEFORE TIME - {before_time}')
        logger.info(f'BEFORE TIME - {time_now}')
        logger.info(f'RANGE ')

        res = pd.date_range(
            min(before_time, time_now),
            max(before_time, time_now)
        ).tolist()
        logger.info(f'RANGE - {[f"{i.month}-{i.day}" for i in res]}')
        days = 0
        for i in res:
            if schedule[str(i.year)][str(i.month)][str(i.day)] == 'Р':
                days += 1
        emp_acceptances = emp.acceptances.filter(acceptance_date__range=[before_time, time_now]).count()
        result['acceptances'] = emp_acceptances
        if days > 0:
            emp_rating = emp_acceptances / days
            result['rating'] = round(emp_rating, 2)
        else:
            emp_rating = 0.0
            result['rating'] = 0.0
        for rating_range in rating_ranges:
            if int(emp_rating * 100) in range(int(rating_range.min_value * 100),
                                                            int(rating_range.max_value * 100) + 1):
                logger.info(f'{emp.name} in {rating_range.name} with qty = {emp_acceptances}')
                result['rating_color'] = rating_range.color
                result['rating_text_color'] = rating_range.text_color
                result['days'] = days
            else:
                logger.info(f'{emp.name} NOT in {rating_range.name} with qty = {emp_acceptances}')
        logger.info(f'{emp.name} - {emp.acceptances.all().count()}')
        results.append(result)
    results = sorted(results, key=lambda x: x['rating'], reverse=True)
    logger.info(f'RESULTS - {results}')
    context = {
        'title': 'Рейтинг сотрудников',
        'results': results
    }
    return render(request, 'rating/rating.html', context)
