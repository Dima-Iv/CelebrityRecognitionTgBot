import cv2
import numpy as np
from keras import models
from keras import backend as K


def load_model(path_to_model: str, path_to_weights: str):
    # Load model from .json
    with open(path_to_model, 'r') as file:
        loaded_model_json = file.read()
    loaded_model = models.model_from_json(loaded_model_json)
    # Load weights from .h5
    loaded_model.load_weights(path_to_weights)
    loaded_model = loaded_model.layers[-2]
    loaded_model = models.Model(inputs=loaded_model.layers[0].input, outputs=loaded_model.layers[-1].output)
    return loaded_model


def get_first_list_item(my_list: list):
    return my_list[0]


def resize_img_pixels_arr(img_pixels):
    return cv2.resize(img_pixels, (64, 64))


def get_pixel_from_img(path_to_img: str):
    return cv2.imread(path_to_img)


def get_vec_from_img(img_pixels, model):
    img_pixels = resize_img_pixels_arr(img_pixels)
    img_pixels = np.asarray([x / 255.0 for x in img_pixels]).astype(np.float32)
    img_pixels = np.expand_dims(img_pixels, axis=0)
    return model.predict(img_pixels)[0, :]


def euclidean_distance(one_img, second_img):
    return K.square(K.sum(K.square(one_img-second_img)))


def find_successful(my_vec, data):
    min_dist = np.inf
    name = ''
    for index, row in data.iterrows():
        dist = euclidean_distance(my_vec, row['img_vec'])
        if min_dist > dist:
            min_dist = dist
            name = row['celebrity_name']
    return name
