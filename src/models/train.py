import os
import librosa
import pandas as pd
import numpy
import tensorflow.keras as keras
from model import SoundAnimalDetector
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from preprocessor import mfcc_spectogram
import datetime


def prepare_data(path, test_size = 0.2):
    """
        Function to prepare data from .csv to
        :param path: to .csv file
        :return: train model
    """

    features = []
    metadata = pd.read_csv(path)

    for index, row in metadata.iterrows():
        class_label = row["class_name"]
        data = mfcc_spectogram(str(row["src"]))
        features.append([data, class_label])

    featuresdf = pd.DataFrame(features, columns=['feature', 'class_label'])

    mfccs = numpy.array(featuresdf.feature.tolist())
    category = numpy.array(featuresdf.class_label.tolist())

    label_encoder = LabelEncoder()
    categories = to_categorical(label_encoder.fit_transform(category))
    print(f'All animal sound categories are: {categories}')

    return train_test_split(mfccs, categories, test_size)


def train(x_train, y_train, num_epochs = 20, num_batch_size = 128):
    x_train, x_test, y_train, y_test = prepare_data('src/data/AnimalSound.csv')
    print(os.path)
    model = SoundAnimalDetector()

    model.fit(x_train,
              y_train,
              batch_size=num_batch_size,
              epochs=num_epochs,
              validation_data=(x_test, y_test),
              callbacks=[keras.callbacks.TensorBoard(
                  log_dir=os.path.join('logs/', str(datetime.datetime.now()))
              )],
              verbose=1)
