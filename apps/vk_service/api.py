import vk


def get_friends_list(access_token):
    session = vk.Session(access_token=access_token)
    api = vk.API(session, v='5.35', lang='ru', timeout=10)
    vk_friends = api.friends.get(fields='first_name, last_name, photo_100')
    friends = [
        {
            'external_id': str(friend['id']),
            'name': '{} {}'.format(friend['first_name'], friend['last_name']),
            'image': friend['photo_100']
        } for friend in vk_friends['items']]
    return friends
