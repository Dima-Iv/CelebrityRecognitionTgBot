from telebot import types

__same_photo_button = 'Найти знаменитость'
__finish_button = 'Закончить'
__back_button = 'Назад'
__delete_one_button = 'Удалить фото'
__delete_all_photos = 'Удалить все фото'

finish = types.ReplyKeyboardMarkup(True, True)
finish.add(__finish_button)

same_delete_or_back = types.ReplyKeyboardMarkup(True)
same_delete_or_back.add(__same_photo_button, __delete_one_button, __delete_all_photos, __back_button)
