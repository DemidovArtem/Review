import matplotlib.pyplot as plt
import requests
import datetime

num_of_seconds = 60 * 60 * 24


def set_data(_data, _beg_date, _step, _num_of_points, _access_key):
    '''Функция, которая получает исторические данные от даты _beg_date
     до даты _beg_date + num_of_steps * _step, где _step - промежуток между датами в днях
     а num_of_steps - колличество точек, которые будут выбраны'''

    params = {'access_key': _access_key,
              'date': _beg_date,
              'currencies': 'EUR', 'format': 1}

    for i in range(_num_of_points):
        if datetime.date.today() > params['date']:
            response = requests.get("http://apilayer.net/api/historical", params=params)
            if response.status_code == 200:
                result = response.json()
                _data[params['date']] = result['quotes']['USDEUR']
                params['date'] = (params['date'] + _step)


def make_extrapolation(_data, _predictions, _step):
    '''Данная функция находит апроксимационную прямую
    по последним точкам графика с помощью линейной регрессии,
    реализованной градиентным спуском. Эта прямая позволят прогнозировать
    стоимость доллара в евро на дату, которая отстоит от последней из считанных
    на время _step'''

    _beg_date = min(_data.keys())

    _start_date = max(_beg_date + step * (num_of_points - 4), _beg_date)

    last_date = max(_data.keys())

    _end_date = last_date + _step

    date_diff = (last_date - _start_date).total_seconds() / num_of_seconds
    
    a = (data[last_date] - data[_start_date]) / date_diff
    b = _data[_start_date]

    alpha = 0.00000001

    eps = 10 ** (-10)

    count = 1000000

    while count > 0:
        for key in _data.keys():
            if key >= _start_date:
                diff_in_date = ((key - _start_date).total_seconds() / num_of_seconds)

                dif_a = 2 * alpha * (_data[key] - (a * diff_in_date + b)) * diff_in_date
                dif_b = 2 * alpha * (_data[key] - (a * diff_in_date + b))

                a -= dif_a
                b -= dif_b

                if abs(dif_a) < eps and abs(dif_b) < eps:
                    break

        count -= 1

    _predictions[_end_date] = a * (_end_date - _start_date).total_seconds() / num_of_seconds + b
    _predictions[_start_date] = b


def draw_results(_data, _predictions):
    '''Данная функция строит график стоимости доллара в евро по
    историческим данным, а так же по значениям,
    предсказанным с помощью впромаксиционной прямой'''
    plt.style.use('seaborn-whitegrid')
    fig = plt.figure(figsize=(19, 7))
    ax = plt.axes()
    ax.plot(_data.keys(), _data.values(), label='Real data')
    ax.plot(_predictions.keys(), _predictions.values(), label='Predicted data', color='g', linestyle='--')
    ax.set_xlabel('Date')
    ax.set_ylabel('USD / EUR')
    plt.show()


data = dict()

print('Введите дату начала интересующего вас периода в формате yyyy mm dd')
[yyyy, mm, dd] = input().split()

beg_date = datetime.date(int(yyyy), int(mm), int(dd))

print('Введите дату окончания интересующего вас периода в формате yyyy mm dd')
[yyyy, mm, dd] = input().split()

print('Введите шаг в днях')

step = datetime.timedelta(days=int(input()))
num_of_points = int((min(datetime.date(int(yyyy), int(mm), int(dd)), datetime.date.today()
                     - datetime.timedelta(days=1)) - beg_date).total_seconds() / step.total_seconds())
access_key = '6ef4b29fd343c489baa9332571337fc1'
predictions = dict()

set_data(data, beg_date, step, num_of_points, access_key)

make_extrapolation(data, predictions, step)

draw_results(data, predictions)
