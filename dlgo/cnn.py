import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from keras.layers import Flatten


np.random.seed(42)
X = np.load('../generated_games/features-40k.npy')
Y = np.load('../generated_games/labels-40k.npy')

num_samples = X.shape[0]
size = 9
input_shape = (size, size, 1)

X = X.reshape(num_samples, size, size, 1)

train_samples = int(0.9 * num_samples)
X_train, X_test = X[:train_samples], X[train_samples:]
Y_train, Y_test = Y[:train_samples], Y[train_samples:]

model = Sequential()
model.add(
    Conv2D(
        filters=48,
        kernel_size=(3, 3),
        activation='sigmoid',
        padding='same'
    )
)
model.add(
    Conv2D(
        48,
        (3, 3),
        padding='same',
        activation='sigmoid'
    )
)
model.add(Flatten())

model.add(
    Dense(
        512,
        activation='sigmoid'
    )
)
model.add(
    Dense(
        size * size,
        activation='sigmoid'
    )
)
model.summary()
