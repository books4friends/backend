import vk

from vk.exceptions import VkAPIError

ERROR_CODE_NOT_SUCCESS_AUTH = 5


def get_friends_list(access_token):
    session = vk.Session(access_token=access_token)
    api = vk.API(session, v='5.35', lang='ru', timeout=10)
    vk_friends = api.friends.get(fields='first_name, last_name, photo_100, city')
    friends = VkAccountSerializer.serialize(vk_friends['items'])
    return friends


def check_token(access_token, vk_id):
    session = vk.Session(access_token=access_token)
    api = vk.API(session, v='5.35', lang='ru', timeout=10)
    try:
        id_from_token = api.users.get()[0]['id']
        return str(id_from_token) == vk_id
    except VkAPIError as e:
        if e.code == ERROR_CODE_NOT_SUCCESS_AUTH:
            return False
        else:
            raise e


def get_user_info(access_token):
    session = vk.Session(access_token=access_token)
    api = vk.API(session, v='5.35', lang='ru', timeout=10)
    user = api.users.get(fields='first_name, last_name, photo_100, city')[0]
    return VkAccountSerializer.serialize(user)


def get_users_info(access_token, user_ids):
    session = vk.Session(access_token=access_token)
    api = vk.API(session, v='5.35', lang='ru', timeout=10)
    user = api.users.get(fields='first_name, last_name, photo_100, city', user_ids=user_ids)
    return VkAccountSerializer.serialize(user)


class VkAccountSerializer:
    @classmethod
    def serialize(cls, obj):
        if isinstance(obj, dict):
            return cls._serialize_one(obj)
        else:
            return cls._serialize_list(obj)

    @classmethod
    def _serialize_one(cls, user):
        return {
            'external_id': str(user['id']),
            'name': '{} {}'.format(user['first_name'], user['last_name']),
            'image': user.get('photo_100'),
            'city': user.get('city', None),
            'link': 'http://vk.com/id{}/'.format(user['id']),
        }

    @classmethod
    def _serialize_list(cls, users):
        return [cls._serialize_one(user) for user in users]
