import os


def view_all_files(message):
    return os.listdir('../users/' + str(message.chat.id) + '/photos')


def delete_all_photos(message):
    for file in view_all_files(message):
        os.remove('../users/' + str(message.chat.id) + '/photos/' + file)