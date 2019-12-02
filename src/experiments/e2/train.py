import os
import pandas as pd
import numpy
import datetime
import logging
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import tensorflow.keras as keras
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Conv2D, MaxPooling2D, Dropout, GlobalAveragePooling2D
import csv

# Update for every experiment
from preprocessor import mfcc_spectogram
from config import get_merged_values
root_path = 'src/experiments/e2/'

def prepare_data(path):
    """
        Function to prepare data from .csv to mfcc spectogram in format DataFrame
        :param path: to .csv file
        :return: data from train model or test it
    """

    features = []
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        logging.info('Dataset loading ...')

        line_count = 0
        for row in csv_reader:
            line_count += 1
            class_label = row[3]
            spectogram_path = row[0].replace('.wav', '.txt')
            exists = os.path.exists(spectogram_path)
            # save data
            if exists:
                data = numpy.loadtxt(spectogram_path)
            else:
                data = mfcc_spectogram(str(row[0]))
                numpy.savetxt(spectogram_path, data)

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

    x_train, x_test, y_train, y_test, num_labels = prepare_data(root_path+'data/experiment2.csv')

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
                  log_dir=os.path.join(root_path+'logs', datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
                  histogram_freq=1,
                  profile_batch=0
              ),
                  keras.callbacks.EarlyStopping(monitor='loss', patience=8),
                  keras.callbacks.LearningRateScheduler(learning_rate)
              ],
              verbose=config['verbose'])


    print('Model is evaluating...')
    result = model.evaluate(x_train, y_train, verbose=0)
    writer = csv.writer(open(root_path + 'result.csv', 'w'))
    writer.writerow(['evaluation_result'])
    with open(root_path + 'result.csv', 'w', newline='') as file:
        writer.writerow([result])

    print('Result of evaluation is: ', result)

    print('Model is saving...')
    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    model.save(f'models/model-{date}.h5')
    print('Model was saved: models/model-', date, '.h5')

    print('Model is predicting ...')
    writer.writerow(['predict_result'])

    predicted_values = model.predict(x_test)
    with open(root_path + 'result.csv', 'w', newline='') as file:
        for value in predicted_values:
            writer.writerow([value])
    print('Result of predict is: ', predicted_values)


def learning_rate(num_epoch):
    config = get_merged_values()

    if config['dynamic_learning_rate'] is False:
        return config['learning_rate']

    num_epoch= config['num_epochs']
    if num_epoch > 5:
        learning_rate = 0.02
    if num_epoch > 15:
        learning_rate = 0.005
    return learning_rate


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    train()
