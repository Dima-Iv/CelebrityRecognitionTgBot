import os
import pandas as pd


def load_data(path_to_data: str):
    df = pd.DataFrame()
    for file in os.listdir(path_to_data):
        pkl = pd.read_pickle(path_to_data + '/' + file)
        df = pd.concat([df, pkl])
    return df
