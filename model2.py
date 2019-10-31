from keras import regularizers
from keras.models import Model
from keras.layers import Dense, Activation, Dropout, Input, Multiply, LSTM, Conv1D
from keras.layers import Flatten, RepeatVector, Permute,  Lambda, Bidirectional, BatchNormalization, Concatenate, GlobalMaxPooling1D
from keras.optimizers import Adam
from keras import backend as K
import tensorflow as tf

def malware_detection_model_2():
    X_input = Input(shape=(1000, 102))

    # Normalization 1
    X = BatchNormalization()(X_input)
    # a = X
    # b = X

    # Gated CNN 1
    a_sig = Conv1D(filters=128, kernel_size=(2), strides=1, kernel_regularizer=regularizers.l2(0.001),
                   activation="sigmoid", padding="same")(X)
    a_relu = Conv1D(filters=128, kernel_size=(2), strides=1, kernel_regularizer=regularizers.l2(0.001),
                    activation="relu", padding="same")(X)
    a = Multiply()([a_sig, a_relu])

    # Gated CNN 2
    b_sig = Conv1D(filters=128, kernel_size=(3), strides=1, kernel_regularizer=regularizers.l2(0.001),
                   activation="sigmoid", padding="same")(X)
    b_relu = Conv1D(filters=128, kernel_size=(3), strides=1, kernel_regularizer=regularizers.l2(0.001),
                    activation="relu", padding="same")(X)
    b = Multiply()([b_sig, b_relu])

    # Concatenate
    X = Concatenate()([a, b])

    # Normalization 2
    X = BatchNormalization()(X)

    # BidirectionalLSTM
    X = Bidirectional(LSTM(100, return_sequences=True))(X)

    #X = GlobalMaxPooling1D()(X)
    
    attention = Dense(1, activation='relu')(X)
    attention = Flatten()(attention)
    attention = Activation('softmax')(attention)
    attention = RepeatVector(200)(attention)
    attention = Permute([2, 1])(attention)

    s_r = Multiply()([X, attention])
    s_r = Lambda(lambda  xin: K.sum(xin, axis=-2), output_shape=(200,))(s_r)

    #X= GlobalMaxPooling1D()(s_r)
    X = Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.001))(s_r)

    X = Dropout(0.5)(X)

    X = Dense(1, kernel_regularizer=regularizers.l2(0.001))(X)
    X = Activation("sigmoid")(X)
    model = Model(inputs=X_input, outputs=X)

    opt = Adam(learning_rate=0.001)
    model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])

    return model
