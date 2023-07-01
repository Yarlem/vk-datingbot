import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import datetime
from core import VkTools
from config import community_token, acces_token
from data import *



class BotInterface():
    def __init__(self, community_token, acces_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0
        self.vkapi = vk_api.VkApi(token=acces_token)

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'attachment': attachment,
                                         'random_id': get_random_id()})

    def check_worksheet(self, event):
        worksheet = self.worksheets.pop()
        while check_user(engine, event.user_id, worksheet["id"]):
            if self.worksheets:
                worksheet = self.worksheets.pop()
            else:
                self.offset += 50
                self.worksheets = self.vkapi.search_worksheet(self.params, self.offset)
                worksheet = self.worksheets.pop()
        return worksheet

    def event_handler(self):
        check_and_create_database(db_url_object)
        Base.metadata.create_all(engine)

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Приветствую, {self.params["name"]}!')

                elif event.text.lower() == 'поиск':
                    self.message_send(event.user_id, 'Начинаю поиск!')
                    self.params = self.vk_tools.get_profile_info(event.user_id)

                    if self.params['city'] is not None:
                        if self.worksheets:
                            # worksheet = self.worksheets.pop()
                            worksheet = self.check_worksheet(event)
                            photos = self.vk_tools.get_photos(worksheet['id'])
                            photo_string = ''
                            for photo in photos:
                                photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        else:
                            self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                            #worksheet = self.worksheets.pop()
                            worksheet = self.check_worksheet(event)
                            photos = self.vk_tools.get_photos(worksheet['id'])
                            photo_string = ''
                            for photo in photos:
                                photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                            self.offset += 50
                    else:
                        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                        if self.params['city'] is None:
                            self.message_send(event.user_id, 'Укажите город поиска')
                            for i in self.longpoll.listen():
                                if i.type == VkEventType.MESSAGE_NEW and i.to_me:
                                    city = i.text.lower()
                                    self.params['city'] = city
                                    break
                                                        
                        if self.params['sex'] is None:
                             s = self.vkapi.method('users.get', {'user_id': event.user_id, 'fields': 'sex'})
                             self.params['sex'] = s


                        if self.params['year'] is None:
                            self.message_send(event.user_id, 'Укажите ваш возраст')
                            for i in self.longpoll.listen():
                                if i.type == VkEventType.MESSAGE_NEW and i.to_me:
                                    year = i.text.lower()
                                    self.params['year'] = int(year)
                                    break


                        worksheet = self.check_worksheet(event)
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'


                    self.message_send(event.user_id, f'имя: {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}', attachment=photo_string)
                    add_user(engine, profile_id = event.user_id , worksheet_id = worksheet['id'])
                    
                else:
                    self.message_send(event.user_id, 'Неизвестная команда')


if __name__ == '__main__':
    bot_interface = BotInterface(community_token, acces_token)
    bot_interface.event_handler()