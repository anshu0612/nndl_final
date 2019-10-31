from keras import regularizers
from keras.models import Model
from keras.layers import Dense, Activation, Dropout, Input, Multiply, LSTM, Conv1D
from keras.layers import Bidirectional, BatchNormalization, Concatenate, GlobalMaxPooling1D
from keras.optimizers import Adam
import tensorflow as tf
from keras import backend as K

def focal_loss(y_true, y_pred):
    gamma = 2.0
    alpha = 0.25
    pt_1 = tf.where(tf.equal(y_true, 1), y_pred, tf.ones_like(y_pred))
    pt_0 = tf.where(tf.equal(y_true, 0), y_pred, tf.zeros_like(y_pred))
    return -K.sum(alpha * K.pow(1. - pt_1, gamma) * K.log(pt_1))-K.sum((1-alpha) * K.pow( pt_0, gamma) * K.log(1. - pt_0))

def malware_detection_model_5():
    X_input = Input(shape=(1000, 102))

    # Normalization 1
    X = BatchNormalization()(X_input)
    # a = X
    # b = X

    # Gated CNN 1
    a_sig = Conv1D(filters=128, kernel_size=(2), strides=1, kernel_regularizer=regularizers.l2(0.0005),
                   activation="sigmoid", padding="same")(X)
    a_relu = Conv1D(filters=128, kernel_size=(2), strides=1, kernel_regularizer=regularizers.l2(0.0005),
                    activation="relu", padding="same")(X)
    a = Multiply()([a_sig, a_relu])

    # Gated CNN 2
    b_sig = Conv1D(filters=128, kernel_size=(3), strides=1, kernel_regularizer=regularizers.l2(0.0005),
                   activation="sigmoid", padding="same")(X)
    b_relu = Conv1D(filters=128, kernel_size=(3), strides=1, kernel_regularizer=regularizers.l2(0.0005),
                    activation="relu", padding="same")(X)
    b = Multiply()([b_sig, b_relu])

    # Concatenate
    X = Concatenate()([a, b])

    # Normalization 2
    X = BatchNormalization()(X)

    # BidirectionalLSTM
    X = Bidirectional(LSTM(100, return_sequences=True))(X)

    X = GlobalMaxPooling1D()(X)

    X = Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.0005))(X)

    X = Dropout(0.5)(X)

    X = Dense(1, kernel_regularizer=regularizers.l2(0.0005))(X)
    X = Activation("sigmoid")(X)
    model = Model(inputs=X_input, outputs=X)

    opt = Adam(learning_rate=0.001, decay=1e-8)
    model.compile(loss=[focal_loss], optimizer=opt, metrics=["accuracy"])

    return model
