import os
import pandas as pd
import numpy
import tensorflow.keras as keras
from model import SoundAnimalDetector
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import datetime
from config import get_merged_values
import logging
from preprocessor import mfcc_spectogram
from keras.models import Sequential
from keras.layers import Dense, Activation, Conv2D, MaxPooling2D, Dropout, GlobalAveragePooling2D


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
    mfccs = numpy.array(featuresdf.feature.tolist())  # creating mfcc spectogram
    category = numpy.array(featuresdf.class_label.tolist())
    label_encoder = LabelEncoder()
    categories = to_categorical(label_encoder.fit_transform(category))
    x_train, x_test, y_train, y_test = train_test_split(mfccs, categories, test_size=0.2)

    return x_train, x_test, y_train, y_test, categories.shape[1]


def create_model(num_labels, num_rows, num_columns, num_channels):
    model = Sequential()
    model.add(Conv2D(filters=16, kernel_size=2, input_shape=(num_rows, num_columns, num_channels), activation='relu'))
    model.add(MaxPooling2D(pool_size=2))
    model.add(Dropout(0.2))

    model.add(Conv2D(filters=32, kernel_size=2, activation='relu'))
    model.add(MaxPooling2D(pool_size=2))
    model.add(Dropout(0.2))

    model.add(Conv2D(filters=64, kernel_size=2, activation='relu'))
    model.add(MaxPooling2D(pool_size=2))
    model.add(Dropout(0.2))

    model.add(Conv2D(filters=128, kernel_size=2, activation='relu'))
    model.add(MaxPooling2D(pool_size=2))
    model.add(Dropout(0.2))
    model.add(GlobalAveragePooling2D())

    model.add(Dense(num_labels, activation='softmax'))
    return model


def train():
    """
        Function to train
        :param  num_epochs: number times that the learning algorithm will work
                num_batch_size: defines the number of samples to work through before updating the internal model parameters
        :return: train model
    """
    config = get_merged_values()

    num_rows = 40
    num_columns = 129
    num_channels = 1

    x_train, x_test, y_train, y_test, num_labels = prepare_data('src/data/AnimalSound.csv')

    x_train = x_train.reshape(x_train.shape[0], num_rows, num_columns, num_channels)
    x_test = x_test.reshape(x_test.shape[0], num_rows, num_columns, num_channels)

    model = create_model(num_labels, num_rows, num_columns, num_channels)

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(x_train,
              y_train,
              batch_size=config['batch_size'],
              epochs=config['num_epochs'],
              validation_data=(x_test, y_test),
              callbacks=[keras.callbacks.TensorBoard(
                  log_dir=os.path.join('logs', datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
                  histogram_freq=1,
                  profile_batch=0
              ),
                  keras.callbacks.EarlyStopping(monitor='loss', patience=8)
              ],
              verbose=config['verbose'])

    print('Model is evaluating...')
    result = model.evaluate(x_train, y_train, verbose=1)
    print('Result of evaluation is: ', result)

    print('Model is saving...')
    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    model.save(f'models/model-{date}.h5')
    print('Model was saved: models/model-',date,'.h5')

    print('Model is predicting ...')
    predicted_values = model.predict(x_test)
    print('Result of predict is: ', predicted_values)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    train()
