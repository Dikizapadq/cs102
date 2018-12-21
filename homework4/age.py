import datetime
from datetime import datetime
from statistics import median
from typing import Optional

from api import get_friends


def age_predict(user_id: int) -> Optional[float]:
    """ Наивный прогноз возраста по возрасту друзей

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: идентификатор пользователя
    :return: медианный возраст пользователя
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    fred = get_friends(user_id,'bdate')
    qwerty = []
    for freed in fred:
        if freed.get('bdate'):
            if len(freed.get('bdate')) >= 8:
              qwerty.append((datetime.today() - datetime.strptime(freed['bdate'], "%d.%m.%Y")).days // 365.25)
    if len(qwerty) == 0:
        return None
    else:
        mediana = median(qwerty)
        return mediana