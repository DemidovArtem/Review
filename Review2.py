"""
Review2 - это программа, которая прогнозирует цену доллара в евро на дату,
отстоящую от последней из полученных данных на заданное пользователем кол-во дней.

Пользователь воодит даты начала и конца интересующего его диапазона, а так же
шаг, на который даты из диапазона будут отстоят друг от друга. Далее программа получает
цены, соответсвующие этим датам, и прогнозирует цену на дату, отстоящую от опследней на значение шага.

Данная программа является прототипом программы, которая получает
данные о ценаpydх валют за последние секунды и прогнозирует цены на доли секунд вперед.
(последняя не была реализована т.к. ключи доступа, которые некоторые ресурсы предоставляют бесплатно,
не позволяют получать данные о текующих ценах
"""

import matplotlib.pyplot as plt
import requests
import datetime

num_of_seconds = 60 * 60 * 24
"""
Глобальная переменная, которая хранит число секнд в сутках,
для перевода из формата timedelta в дни (т.к. в timedelta 
есть встроенная функция total_seconds())
"""


def set_data(_data, _beg_date, _step, _num_of_points, _access_key):
    """
     Данная функция получает исторические данные от даты _beg_date
     до даты _beg_date + num_of_steps * _step, где _step - промежуток между датами в днях
     а num_of_steps - колличество точек, которые будут выбраны. Параметр _access_key
     задает ключ доступа, который позволяет получать данные с помощью get-запросов

     :_data: dict
     :_beg_date: date
     :_step: temedelta
     :_num_of_points: int
     :_access_key: string

     :return: None
     """

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
    """
    Данная функция находит апроксимационную прямую
    по последним точкам графика с помощью линейной регрессии,
    реализованной градиентным спуском. Эта прямая позволят прогнозировать
    стоимость доллара в евро на дату, которая отстоит от последней из считанных
    на время _step

    :_data: dict
    :_predictions: dict
    :step: timedelta

    :return: None
    """

    _beg_date = min(_data.keys())

    last_date = max(_data.keys())

    _start_date = max(last_date - _step * 3, _beg_date)

    _end_date = last_date + _step

    date_diff = (last_date - _start_date).total_seconds() / num_of_seconds

    a = (_data[last_date] - _data[_start_date]) / date_diff
    b = _data[_start_date]

    alpha = 0.000001

    eps = 10 ** (-10)

    count = 1000000

    dif_a = 0
    dif_b = 0

    while count > 0:
        for key in _data.keys():
            if key > _start_date:
                diff_in_date = ((key - _start_date).total_seconds() / num_of_seconds)

                dif_a += -2 * alpha * (_data[key] - (a * diff_in_date + b)) * diff_in_date
                dif_b += -2 * alpha * (_data[key] - (a * diff_in_date + b))

        if abs(dif_a) < eps and abs(dif_b) < eps:
            break
        else:
            a -= dif_a
            b -= dif_b
            dif_a = 0
            dif_b = 0

        count -= 1

    _predictions[_end_date] = a * (_end_date - _start_date).total_seconds() / num_of_seconds + b
    _predictions[_start_date] = b


def draw_results(_data, _predictions):
    """
    Данная функция строит график стоимости доллара в евро по
    историческим данным, а так же по значениям,
    предсказанным с помощью впромаксиционной прямой.

    :_data: dict
    :_predictions: dict

    :return: None
    """

    plt.style.use('seaborn-whitegrid')
    fig = plt.figure(figsize=(19, 7))
    ax = plt.axes()
    ax.plot(_data.keys(), _data.values(), label='Real data')
    ax.plot(_predictions.keys(), _predictions.values(), label='Predicted data', color='g', linestyle='--')
    ax.set_xlabel('Date')
    ax.set_ylabel('USD / EUR')
    plt.show()


def main():

    """
    Позволяет пользователю получить данные за указанный промежуток
    с указанным шагом. В то же время строит апромаксиционную прямую,
    которую вместе с реальными данными откладывает в осяц цена
    дата. Полученный график выводится на экран

    :return: None
    """
    print('Введите дату начала интересующего вас периода в формате yyyy mm dd')
    [yyyy, mm, dd] = input().split()

    beg_date = datetime.date(int(yyyy), int(mm), int(dd))

    print('Введите дату окончания интересующего вас периода в формате yyyy mm dd')
    [yyyy, mm, dd] = input().split()

    print('Введите шаг в днях')

    data = dict()

    step = datetime.timedelta(days=int(input()))
    num_of_points = int((min(datetime.date(int(yyyy), int(mm), int(dd)), datetime.date.today()
                         - datetime.timedelta(days=1)) - beg_date).total_seconds() / step.total_seconds()) + 1
    access_key = '6ef4b29fd343c489baa9332571337fc1'
    predictions = dict()

    set_data(data, beg_date, step, num_of_points, access_key)

    make_extrapolation(data, predictions, step)

    draw_results(data, predictions)


if __name__ == "__main__":
    main()
