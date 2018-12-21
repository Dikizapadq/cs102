import requests
import time

import config


def get(url, params={}, timeout=5, max_retries=5, backoff_factor=0.3):
    """ Выполнить GET-запрос

    :param url: адрес, на который необходимо выполнить запрос
    :param params: параметры запроса
    :param timeout: максимальное время ожидания ответа от сервера
    :param max_retries: максимальное число повторных запросов
    :param backoff_factor: коэффициент экспоненциального нарастания задержки
    """
    for retry in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            return response
        except requests.exceptions.RequestException:
            if retry == max_retries - 1:
                raise
            backoff_value = backoff_factor * (2 ** retry)
            time.sleep(backoff_value)


def get_friends(user_id, fields):
    """ Вернуть данных о друзьях пользователя

    :param user_id: идентификатор пользователя, список друзей которого нужно получить
    :param fields: список полей, которые нужно получить для каждого пользователя
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert isinstance(fields, str), "fields must be string"
    assert user_id > 0, "user_id must be positive integer"
    query_params = {
        'domain': config.VK_CONFIG['domain'],
        'access_token': config.VK_CONFIG['access_token'],
        'user_id': user_id,
        'fields': fields,
        'v': config.VK_CONFIG['version']
    }

    url = "{}/friends.get".format(query_params['domain'])
    response = get(url, params=query_params)
    qq = response.json()
    fail = qq.get('error')
    if fail:
        friends = response.json()
        return friends
    friends = response.json()['response']['items']
    time.sleep(0.2)
    return friends


def messages_get_history(user_id, offset=0, count=20):
    """ Получить историю переписки с указанным пользователем

    :param user_id: идентификатор пользователя, с которым нужно получить историю переписки
    :param offset: смещение в истории переписки
    :param count: число сообщений, которое нужно получить
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    assert isinstance(offset, int), "offset must be positive integer"
    assert offset >= 0, "user_id must be positive integer"
    assert count >= 0, "user_id must be positive integer"
    query_params = {
        'domain': config.VK_CONFIG['domain'],
        'access_token': config.VK_CONFIG['access_token'],
        'user_id': user_id,
        'offset': offset,
        'count': count,
        'v': config.VK_CONFIG['version']
    }

    url = "{}/messages.getHistory".format(query_params['domain'])
    response = get(url, params=query_params)
    qq = response.json()
    fail = qq.get('error')
    if fail:
        massages = response.json()
        return massages
    massages = response.json()['response']['items']
    time.sleep(0.3)
    return massages

def names(user_id: int) -> list:
    namelist: list = []
    users = get_friends(user_id, "first_name, last_name")
    for i in users:
        if i['first_name'] == 'DELETED':
            continue
        else:
            name = [i['first_name'], i['last_name']]
            nam = str(name)
            nam = nam.replace("[", "")
            nam = nam.replace("'", "")
            nam = nam.replace("]", "")
            nam = nam.replace(",", "")
            namelist.append(nam)
    return namelist
