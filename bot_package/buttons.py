from telebot import types


__same_photo_button = 'Найти похожую знаменитость'
'''__find_something_button = 'Что на фото?'''
__finish_button = 'Закончить'
__back_button = 'Назад'
__delete_button = 'Удалить фото'

finish_photo = types.ReplyKeyboardMarkup(True, True)
finish_photo.add(__finish_button)

find_or_same_face = types.ReplyKeyboardMarkup(True)
find_or_same_face.add(__same_photo_button, __delete_button, __back_button)
