import os
import pandas as pd
import numpy
import tensorflow.keras as keras
from model import SoundAnimalDetector
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import datetime
from preprocessor import mfcc_spectogram

def prepare_data(path):
    """
        Function to prepare data from .csv to mfcc spectogram in format DataFrame
        :param path: to .csv file
        :return: data from train model or test it
    """

    features = []
    metadata = pd.read_csv(path)

    for index, row in metadata.iterrows():
        class_label = row["class_name"]
        data = mfcc_spectogram(str(row["src"]))
        features.append([data, class_label])

    featuresdf = pd.DataFrame(features, columns=['feature', 'class_label'])
    mfccs = numpy.array(featuresdf.feature.tolist()) # creating mfcc spectogram
    category = numpy.array(featuresdf.class_label.tolist())
    label_encoder = LabelEncoder()
    categories = to_categorical(label_encoder.fit_transform(category))

    print(f'Count of animal are: {categories.length}')

    return train_test_split(mfccs, categories, test_size = 0.2)


def train(num_epochs = 20, num_batch_size = 128):
    """
        Function to train
        :param  num_epochs: number times that the learning algorithm will work
                num_batch_size: defines the number of samples to work through before updating the internal model parameters
        :return: train model
    """
    num_rows = 10
    num_columns = 4
    num_channels = 1

    x_train, x_test, y_train, y_test = prepare_data('src/data/AnimalSound.csv')
    x_train = x_train.reshape(x_train.shape[0], num_rows, num_columns, num_channels)
    x_test = x_test.reshape(x_test.shape[0], num_rows, num_columns, num_channels)

    model = SoundAnimalDetector(dim_output=len(x_train))
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    model.fit(x_train,
              y_train,
              batch_size=num_batch_size,
              epochs=num_epochs,
              validation_data=(x_test, y_test),
              callbacks=[keras.callbacks.TensorBoard(
                  log_dir=os.path.join('logs', datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
                  histogram_freq=1,
                  profile_batch=0
              )],
              verbose=1)