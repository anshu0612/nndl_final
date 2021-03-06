from keras import regularizers
from keras.models import Model
from keras.layers import Dense, Activation, Dropout, Input, Conv1D
from keras.layers import BatchNormalization, GlobalMaxPooling1D
from keras.optimizers import Adam

def malware_detection_model_1():
    X_input = Input(shape=(1000, 102))

    X = BatchNormalization()(X_input)

    X = Conv1D(filters=128, kernel_size=(2), strides=1, kernel_regularizer=regularizers.l2(0.0005),
                   activation="sigmoid", padding="same")(X)

    X = GlobalMaxPooling1D()(X)
    X = Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.0005))(X)
    X = Dropout(0.5)(X)

    X = Dense(1, kernel_regularizer=regularizers.l2(0.0005))(X)
    X = Activation("sigmoid")(X)
    model = Model(inputs=X_input, outputs=X)

    opt = Adam(learning_rate=0.001, decay=1e-8)
    model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])

    return model
