from keras import regularizers
from keras.models import Model
from keras.layers import Dense, Activation, Dropout, Input, Multiply, LSTM, Conv1D, Flatten, \
    RepeatVector, Permute, Lambda
from keras.layers import Reshape, Bidirectional, BatchNormalization, Concatenate, GlobalMaxPooling1D
from keras.optimizers import Adam, SGD
from keras import backend as K
from keras.layers import merge

def attention_3d_block(inputs):
    # inputs.shape = (batch_size, time_steps, input_dim)
    input_dim = int(inputs.shape[2])
    a = Permute((2, 1))(inputs)
    a = Reshape((input_dim, 1000))(a) # this line is not useful. It's just to know which dimension is what.
    a = Dense(1000, activation='softmax')(a)
    if True:
        a = Lambda(lambda x: K.mean(x, axis=1), name='dim_reduction')(a)
        a = RepeatVector(input_dim)(a)
    a_probs = Permute((2, 1), name='attention_vec')(a)
    output_attention_mul = Concatenate(name='attention_mul')([inputs, a_probs])
    return output_attention_mul


def malware_detection_model_1():
    X_input = Input(shape=(1000, 102))

    # Normalization 1
    X = BatchNormalization()(X_input)

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

    # attention = Dense(1, activation='tanh')(X)
    # attention = Flatten()(attention)
    # attention = Activation('softmax')(attention)
    # attention = RepeatVector(200)(attention)
    # attention = Permute([2, 1])(attention)
    #
    # s_r = Multiply()([X, attention])
    # s_r = Lambda(lambda  xin: K.sum(xin, axis=-2), output_shape=(200,))(s_r)

    # attention_probs = Dense(1, activation='softmax', name='attention_vec')(X)
    # attention_mul = merge([X, attention_probs], output_shape=32, name='attention_mul', mode='mul')
    attention_mul = attention_3d_block(X)
    # X = GlobalMaxPooling1D()(X)
    print("COMIDSNFKSNFKJHFKJHASDSA", attention_mul.shape)
    X = Flatten()(attention_mul)
    X = Dense(1, activation='sigmoid', kernel_regularizer=regularizers.l2(0.0005))(X)
    # X = Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.0005))(attention_mul)
    #
    # X = Dropout(0.5)(X)
    #
    # X = Dense(1, kernel_regularizer=regularizers.l2(0.0005))(X)
    # X = Activation("sigmoid")(X)
    model = Model(inputs=X_input, outputs=X)

    opt = SGD(learning_rate=0.001, decay=1e-8, momentum=0.9)
    model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])

    return model
