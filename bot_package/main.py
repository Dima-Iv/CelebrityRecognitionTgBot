import os
import re
import telebot
from dotenv import load_dotenv
from bot_package import buttons
from bot_package.utils import view_all_files, delete_all_photos

from data_management_package.prepare_data import load_data
from data_management_package.utils import load_model, get_pixel_from_img, get_vec_from_img, find_successful

# Read token
load_dotenv()
__TOKEN = os.getenv('TOKEN')

nums = re.compile(r'\d+')


def main():
    bot = telebot.TeleBot(__TOKEN)
    df_data = load_data('../data')
    path_to_model = '../nn_model/model.json'
    path_to_weights = '../nn_model/nn_weights.h5'

    def delete_one_photo(message, file_name_nums):
        try:
            num = int(message.text)
            os.remove('../users/' + str(message.chat.id) + '/photos/' + file_name_nums[num])
            bot.send_message(message.chat.id, text='Я удалил файл')
        except (KeyError, ValueError):
            bot.send_message(message.chat.id, text='Что-то не то. Попробуй еще раз'
                                                   '(подсказываю, вводи числа только из предложенных)')

    def find_celebrity(message, file_name_nums):
        try:
            num = int(message.text)
            name_img = file_name_nums[num]

            model = load_model(path_to_model, path_to_weights)

            my_pixel_img = get_pixel_from_img('../users/' + str(message.chat.id) + '/photos/' + name_img)
            vec_from_img = get_vec_from_img(my_pixel_img, model)

            celebrity_name = find_successful(vec_from_img, df_data)
            bot.send_message(message.chat.id, text=celebrity_name)
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
                         reply_markup=buttons.finish)

    @bot.message_handler(content_types=['photo'])
    def add_photo(message):
        try:
            os.makedirs('../users/' + str(message.chat.id) + '/photos', mode=0o777, exist_ok=True)
            count_of_photos = len(view_all_files(message))
            if count_of_photos < 10:
                file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                path_to_photo = '../users/' + str(message.chat.id) + '/' + file_info.file_path
                with open(path_to_photo, 'wb') as new_file:
                    new_file.write(downloaded_file)
                bot.reply_to(message, f'Фото добавлено, как {nums.findall(file_info.file_path)}',
                             reply_markup=buttons.same_delete_or_back)
            else:
                bot.send_message(message.chat.id, text='Удалите одно из фото.',
                                 reply_markup=buttons.same_delete_or_back)
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
        elif message.text.lower() == 'найти знаменитость':
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
        elif message.text.lower() == 'удалить все фото':
            delete_all_photos(message)
            bot.send_message(message.chat.id, text='Я удалил все ваши фото')
        elif message.text.lower() == 'назад':
            bot.send_message(message.chat.id, text='Вернул\nДобавьте новое фото \U0001F603 или прощаемся \U0001F614',
                             reply_markup=buttons.finish)
        else:
            bot.send_message(message.chat.id, text='Не могу ничем помочь. Я не понимаю\U0001F61E')

    bot.polling(none_stop=True, interval=0)


# Start telegram bot
if __name__ == '__main__':
    main()
