import tensorflow.keras as keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, MaxPooling2D, Dropout, Conv2D, GlobalAveragePooling2D

class SoundAnimalDetector(keras.Model):
    def __init__(self, dim_output, num_rows, num_columns, num_channels):
        super(SoundAnimalDetector, self).__init__()

        self.model = Sequential()
        self.model.add(
            Conv2D(filters=16, kernel_size=2, input_shape=(num_rows, num_columns, num_channels), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=2))
        self.model.add(Dropout(0.2))

        self.model.add(Conv2D(filters=32, kernel_size=2, activation='relu'))
        self.model.add(MaxPooling2D(pool_size=2))
        self.model.add(Dropout(0.2))

        self.model.add(Conv2D(filters=64, kernel_size=2, activation='relu'))
        self.model.add(MaxPooling2D(pool_size=2))
        self.model.add(Dropout(0.2))

        self.model.add(Conv2D(filters=128, kernel_size=2, activation='relu'))
        self.model.add(MaxPooling2D(pool_size=2))
        self.model.add(Dropout(0.2))
        self.model.add(GlobalAveragePooling2D())

        self.model.add(Dense(dim_output, activation='softmax'))
