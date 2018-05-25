import matplotlib.pyplot as plt
import requests
import datetime

num_of_seconds = 60 * 60 * 24


def set_data(_data, _beg_date, _step, _num_of_points, _access_key):

    params = {'access_key': _access_key,
              'date': _beg_date,
              'currencies': 'EUR', 'format': 1}

    for i in range(_num_of_points):
        response = requests.get("http://apilayer.net/api/historical", params=params)
        result = response.json()
        _data[params['date']] = result['quotes']['USDEUR']
        params['date'] = (params['date'] + _step)


def make_extrapolation(_data, _predictions, _start_date, _end_date, _step):

    last_date = max(_data.keys())

    norm = (last_date - _start_date).total_seconds() / num_of_seconds

    a = 1
    b = _data[start_date]

    alpha = 0.00000001

    eps = 10 ** (-10)

    count = 1000000

    while count > 0:
        for key in _data.keys():
            if key >= _start_date:
                diff_in_date = ((key - _start_date).total_seconds() / num_of_seconds) / norm

                dif_a = 2 * alpha * (_data[key] - (a * diff_in_date + b)) * diff_in_date
                dif_b = 2 * alpha * (_data[key] - (a * diff_in_date + b))

                a -= dif_a
                b -= dif_b

                if abs(dif_a) < eps and abs(dif_b) < eps:
                    break

        count -= 1

    _predictions[_end_date] = norm * a * (_end_date - _start_date).total_seconds() / num_of_seconds + b

    _predictions[_start_date] = b


def draw_results(_data, _predictions):
    plt.style.use('seaborn-whitegrid')
    fig = plt.figure(figsize=(19, 7))
    ax = plt.axes()
    ax.plot(_data.keys(), _data.values(), label='Real data')
    ax.plot(_predictions.keys(), _predictions.values(), label='Predicted data', color='g', linestyle='--')
    ax.set_xlabel('Date')
    ax.set_ylabel('USD / EUR')


data = dict()
beg_date = datetime.date(1999, 1, 31)
step = datetime.timedelta(days=10)
num_of_points = 8
access_key = '6ef4b29fd343c489baa9332571337fc1'

set_data(data, beg_date, step, num_of_points, access_key)

predictions = dict()

end_date = beg_date + step * num_of_points

start_date = beg_date + step * (num_of_points - 3)

make_extrapolation(data, predictions, start_date, end_date, step)

draw_results(data, predictions)
