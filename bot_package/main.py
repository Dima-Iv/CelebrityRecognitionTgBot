import bot_package.bot_abilities
from conv_nn.keras_conv_nn import load_model
from conv_nn.work_with_dataset import get_data_frame
import pandas as pd


__MODEL_AND_WEIGHT_DIR = 'C:/Users/Dima/PycharmProjects/CourseWorkTelegramBotAndNN/data/drive-download' \
                         '-20201015T131447Z-001/ '
model = load_model(__MODEL_AND_WEIGHT_DIR + 'model1.json', __MODEL_AND_WEIGHT_DIR + 'nn_weights1.h5')
df = get_data_frame()
excel_df = pd.read_excel('C:/Users/Dima/PycharmProjects/CourseWorkTelegramBotAndNN/conv_nn/l_a_n.xlsx')


def main():
    telegram_bot = bot_package.bot_abilities.bot
    telegram_bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
