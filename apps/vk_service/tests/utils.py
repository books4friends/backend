import uuid
import random


def generate_vk_user():
    vk_id = str(uuid.uuid4())
    city_variant = random.randint(0, 2)
    if city_variant == 0:
        city = None
    elif city_variant == 1:
        city = {'id': 2, 'title': 'Санкт-Петербург'}
    else:
        city = {'id': 151, 'title': 'Уфа'}
    return {
        'external_id': vk_id,
        'name': vk_id[0:6],
        'image': 'https://vk.com/images/camera_100.png?ava=1',
        'city': city
    }


def generate_vk_users(count):
    return [generate_vk_user() for i in range(count)]
