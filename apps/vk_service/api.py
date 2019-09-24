import vk

from vk.exceptions import VkAPIError

ERROR_CODE_NOT_SUCCESS_AUTH = 5


def get_friends_list(access_token):
    session = vk.Session(access_token=access_token)
    api = vk.API(session, v='5.35', lang='ru', timeout=10)
    vk_friends = api.friends.get(fields='first_name, last_name, photo_100, city')
    friends = [
        {
            'external_id': str(friend['id']),
            'name': '{} {}'.format(friend['first_name'], friend['last_name']),
            'image': friend.get('photo_100'),
            'city': friend.get('city', None),
            'link': 'http://vk.com/id{}/'.format(friend['id']),
        } for friend in vk_friends['items']]
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
