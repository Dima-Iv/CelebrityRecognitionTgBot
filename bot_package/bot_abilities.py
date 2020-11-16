import os
import re

import cv2
import numpy as np
import telebot

from bot_package import buttons
from bot_package.main import excel_df, df, model
from conv_nn.work_with_dataset import imdb_dir

__TOKEN = '1355443919:AAEgy1ZhpDR0K6SScJRw4bJbABJ18ookeVY'
nums = re.compile(r'\d+')
bot = telebot.TeleBot(__TOKEN)


def resize_img_pixels_arr(img_pixels):
    return cv2.resize(img_pixels, (64, 64))


def view_all_files(message):
    return os.listdir('C:/Users/Dima/PycharmProjects/CourseWorkTelegramBotAndNN/users/'
                      + str(message.chat.id) + '/photos')


def delete_all_photos(message):
    for file in view_all_files(message):
        os.remove('C:/Users/Dima/PycharmProjects/CourseWorkTelegramBotAndNN/users/'
                  + str(message.chat.id) + '/photos/' + file)


def delete_one_photo(message, file_name_nums):
    try:
        num = int(message.text)
        os.remove('C:/Users/Dima/PycharmProjects/CourseWorkTelegramBotAndNN/users/'
                  + str(message.chat.id) + '/photos/' + file_name_nums[num])
        bot.send_message(message.chat.id, text='Я удалил файл')
    except (KeyError, ValueError):
        bot.send_message(message.chat.id, text='Что-то не то. Попробуй еще раз'
                                               '(подсказываю, вводи числа только из предложенных)')


def find_celebrity(message, file_name_nums):
    try:
        num = int(message.text)
        name_img = file_name_nums[num]
        my_img_st_pixels = cv2.imread('C:/Users/Dima/PycharmProjects/CourseWorkTelegramBotAndNN/users/'
                                      + str(message.chat.id) + '/photos/' + name_img)
        my_img_sec_pixels = resize_img_pixels_arr(my_img_st_pixels).astype(np.float32)
        my_img_sec_pixels = np.expand_dims(my_img_sec_pixels, axis=0)
        prediction = model.predict(my_img_sec_pixels)
        result = np.where(prediction[0] == 1)[0][0]
        celebrity_name = excel_df[excel_df['num'] == result]['label'].iloc[0]
        path_to_celebrity_img = df[df['celebrity_name'] == celebrity_name]['full_path'].iloc[0][0]
        with open(imdb_dir + path_to_celebrity_img, 'rb') as file:
            img = file.read()
        bot.send_photo(message.chat.id, photo=img
                       , caption=celebrity_name)
    except IndexError:
        bot.send_message(message.chat.id, text='Я не знаю людей похожих на тебя(')
    except (KeyError, ValueError, TypeError):
        bot.send_message(message.chat.id, text='Что-то не то. Попробуй еще раз'
                                               '(подсказываю, вводи числа только из предложенных)')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     f'Привет {message.from_user.username}, этот бот '
                     f'может найти знаменитость на которую ты похож '
                     f'и преобразовать твою фотографию. '
                     f'Добавьте своё фото\U0001F64F'
                     f'(их должно быть не больше 10)',
                     reply_markup=buttons.finish_photo)


@bot.message_handler(content_types=['photo'])
def add_photo(message):
    try:
        count_of_photos = len(view_all_files(message))
        if count_of_photos < 10:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            os.makedirs('C:/Users/Dima/PycharmProjects/CourseWorkTelegramBotAndNN/users/'
                        + str(message.chat.id) + '/photos'
                        , mode=0o777, exist_ok=True)
            path_to_photo = 'C:/Users/Dima/PycharmProjects/CourseWorkTelegramBotAndNN/users/' \
                            + str(message.chat.id) + '/' + file_info.file_path
            with open(path_to_photo, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.reply_to(message, f'Фото добавлено, как {nums.findall(file_info.file_path)}'
                         , reply_markup=buttons.find_or_same_face)
        else:
            bot.send_message(message.chat.id, text='Удалите одно из фото.',
                             reply_markup=buttons.find_or_same_face)
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(content_types=['text'])
def choose_message(message):
    if message.text.lower() == 'закончить':
        try:
            delete_all_photos(message)
            bot.send_message(message.chat.id, text='Обращайтесь еще \U0001F609')
        except FileNotFoundError:
            bot.send_message(message.chat.id, text='Могли хотя бы попробовать \U0001F614')
    elif message.text.lower() == 'найти похожую знаменитость':
        file_name_nums = {}
        for file_name in view_all_files(message):
            file_name_nums[int(nums.findall(file_name)[0])] = file_name
        bot.send_message(message.chat.id, text=f'Введите номер фото, '
                                               f'с которым хотите работать:\n{list(file_name_nums.keys())}')
        bot.register_next_step_handler(message, find_celebrity, file_name_nums)
    elif message.text.lower() == 'улучшить фото':
        pass
    elif message.text.lower() == 'удалить фото':
        file_name_nums = {}
        for file_name in view_all_files(message):
            file_name_nums[int(nums.findall(file_name)[0])] = file_name
        bot.send_message(message.chat.id, text=f'Введите номер:\n{list(file_name_nums.keys())}')
        bot.register_next_step_handler(message, delete_one_photo, file_name_nums)
    elif message.text.lower() == 'назад':
        bot.send_message(message.chat.id, text='Вернул\nДобавьте новое фото \U0001F603 или прощаемся \U0001F614',
                         reply_markup=buttons.finish_photo)
    else:
        bot.send_message(message.chat.id, text='Не могу ничем помочь. Я не понимаю\U0001F61E')
