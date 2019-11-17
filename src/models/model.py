import tensorflow.keras as keras

class SoundAnimalDetector(keras.Model):
    def __init__(self, dim_output):
        super(SoundAnimalDetector, self).__init__()

        self.model_layers = [
            keras.layers.Conv2D(
                filters=1,
                kernel_size=3,
                padding='same',
                activation='relu'),
            keras.layers.MaxPooling2D(pool_size=(2, 2)),

            keras.layers.Conv2D(
                filters=32,
                kernel_size=3,
                padding='same',
                activation='relu'),
            keras.layers.MaxPooling2D(pool_size=(2, 2)),

            keras.layers.Conv2D(
                filters=64,
                kernel_size=3,
                padding='same',
                activation='relu'),
            keras.layers.MaxPooling2D(pool_size=(2, 2)),

            keras.layers.Flatten(),

            keras.layers.Dense(
                units=512,
                activation='relu'),

            keras.layers.Dense(
                units=dim_output,
                activation='softmax')
        ]

    def call(self, x):
        for layer in self.model_layers:
            x = layer(x)
            return x
