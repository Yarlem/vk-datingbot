import vk_api
from vk_api.exceptions import ApiError
from config import acces_token
from datetime import datetime


class VkTools:
    def __init__(self, acces_token):
        self.vkapi = vk_api.VkApi(token=acces_token)

    def _bdate_to_year(self, bdate):
        user_year = bdate.split('.')[2] if bdate is not None else None
        now = datetime.now().year
        return now - int(user_year)


    def get_profile_info(self, user_id):

        try:
            info, = self.vkapi.method('users.get', {'user_id': user_id, 'fields': 'city,bdate,sex,relation,home_town'})
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if 'first_name' in info and 'last_name' in info else None, 
                  'sex': info.get('sex'), 
                  'id': info.get('user_id'),
                  'city': info.get('city')['title'] if info.get('city') is not None else None, 
                  'year': self._bdate_to_year(info.get('bdate'))}
        return result

    def search_worksheet(self, params, offset=0):
        try:
            users = self.vkapi.method('users.search',
                                    {'count': 50,
                                    'hometown': params['city'],
                                    'offset': offset,
                                    'sex': 1 if params['sex'] == 2 else 2,
                                    'has_photo': True,
                                    'age_from': params['year'] - 5,
                                    'age_to': params['year'] + 5 })
        except ApiError as e:
            users = []
            print(f'error = {e}')
            
        result = [{'name': item['first_name'] + ' ' + item['last_name'],
                   'id': item['id']} for item in users['items'] if item['is_closed'] is False]
        return result

    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get', {
                'owner_id': id,
                'album_id': 'profile',
                'extended': 1
            })
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']} for item in photos['items']]
        result.sort(key=lambda x: x["likes"] + x["comments"], reverse=True)
        return result[:3]
        





# if __name__ == '__main__':
#     user_id = 810732397
#     vk_tools = VkTools(acces_token)
#     params = vk_tools.get_profile_info(user_id)
#     worksheets = vk_tools.search_worksheet(params, 15)
#     worksheet = worksheets.pop()
#     photo = vk_tools.get_photos(worksheet['id'])
#     print(photo)
