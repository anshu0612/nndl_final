import numpy as np
import math
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from keras import regularizers
from keras.models import Model, load_model
from keras.layers import Dense, Activation, Dropout, Input, Multiply, TimeDistributed, LSTM, Conv1D, Flatten, \
    RepeatVector, Permute, Lambda
from keras.layers import Bidirectional, BatchNormalization, Concatenate, GlobalMaxPooling1D
from keras.optimizers import Adam, SGD
from keras.losses import binary_crossentropy
from keras.callbacks.callbacks import TerminateOnNaN, ModelCheckpoint, LearningRateScheduler, ReduceLROnPlateau, \
    EarlyStopping
from keras import backend as K
import tensorflow as tf

'''
    STEP 1 : Getting training sample
'''
train_samples = 18622
# 18622
test_samples = 6051
# 6051
batch_size = 128
no_epochs = 30
n_x = 102

# max length of a sequence
max_Tx = 1000
X_train = []

for i in range(0, train_samples):
    data = np.load("data/train/train/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, 102))
    zero_mat[:data.shape[0], :] = data
    X_train.append(zero_mat)

X_train = np.array(X_train)

df = pd.read_csv("data/train_kaggle.csv", usecols=["Label"])
Y_train = df[:train_samples]
Y_train = Y_train.values

kfolds = StratifiedKFold(n_splits=2,  shuffle=True, random_state=1)
# list(StratifiedKFold(n_splits=4, shuffle=False, random_state=1).split(X_train, Y_train))
print(X_train.shape, Y_train.shape)

'''
    STEP 2 : model
'''


def malware_detection_model(input_shape):
    X_input = Input(shape=input_shape)

    # Normalization 1
    X = BatchNormalization()(X_input)
    # a = X
    # b = X

    # Gated CNN 1
    a_sig = Conv1D(filters=128, kernel_size=(2), strides=1,activity_regularizer=regularizers.l2(0.01),  kernel_regularizer=regularizers.l2(0.0005),
                   activation="sigmoid", padding="same")(X)
    a_relu = Conv1D(filters=128, kernel_size=(2), strides=1, kernel_regularizer=regularizers.l2(0.0005), activation="relu", padding="same")(X)
    a = Multiply()([a_sig, a_relu])

    # Gated CNN 2
    b_sig = Conv1D(filters=128, kernel_size=(3), strides=1, activity_regularizer=regularizers.l2(0.01),  kernel_regularizer=regularizers.l2(0.0005),
                   activation="sigmoid", padding="same")(X)
    b_relu = Conv1D(filters=128, kernel_size=(3), strides=1, kernel_regularizer=regularizers.l2(0.0005), activation="relu" 
                    ,padding="same")(X)
    # b = Conv1D(filters=128, kernel_size=3, strides=1)(b)
    b = Multiply()([b_sig, b_relu])

    # Concatenate
    X = Concatenate()([a, b])

    # Normalization 2
    X = BatchNormalization()(X)

    # BidirectionalLSTM
    X = Bidirectional(LSTM(100, return_sequences=True))(X)

    X = GlobalMaxPooling1D()(X)
    # attention = Dense(1, activation='tanh')(X)
    # attention = Flatten()(attention)
    # attention = Activation('softmax')(attention)
    # attention = RepeatVector(200)(attention)
    # attention = Permute([2, 1])(attention)

    # s_r = Multiply()([X, attention])
    # s_r = Lambda(lambda  xin: K.sum(xin, axis=-2), output_shape=(200,))(s_r)

    X = Dense(64, activation='relu', activity_regularizer=regularizers.l2(0.01), kernel_regularizer=regularizers.l2(0.0005))(X)

    X = Dropout(0.5)(X)

    X = Dense(1)(X)
    X = Activation("sigmoid")(X)
    model = Model(inputs=X_input, outputs=X)

    return model


'''
    STEP 3 : Train model
'''
num_samples = X_train.shape[0]

# https://stackoverflow.com/questions/39779710/setting-up-a-learningratescheduler-in-keras
# learning_scheduler = LearningRateScheduler()


def generate_data(x_data, y_data, b_size):
    samples_per_epoch = x_data.shape[0]
    number_of_batches = samples_per_epoch / b_size
    counter = 0
    while 1:
        x_batch = np.array(x_data[batch_size * counter:batch_size * (counter + 1)])
        y_batch = np.array(y_data[batch_size * counter:batch_size * (counter + 1)])
        counter += 1
        yield x_batch, y_batch

        if counter >= number_of_batches:
            counter = 0

def lrs_Decay(epoch):
    if epoch >= 10 and epoch <=20:
        print("LR 0.001")
        return 0.001
    elif epoch >20:
        print("LR 0.0001")
        return 0.0001
    print("print 0.01")
    return 0.01
    
lrs = LearningRateScheduler(lrs_Decay)
i = 1
for train, test in kfolds.split(X_train, Y_train):
    print('\nFold', i)
    generator2 = generate_data(X_train[train], Y_train[train], batch_size)
    reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=12, verbose=1, mode='min')
    terminate_on_nan = TerminateOnNaN()
    model_checkpoint = ModelCheckpoint("cpKFoldv3", monitor='loss', save_best_only=True, mode='min')
    early_stopping = EarlyStopping(monitor='loss', patience=12, mode='auto')

    model = malware_detection_model(input_shape=(1000, n_x))
    opt = Adam(learning_rate=0.01)
    model.compile(loss='binary_crossentropy', optimizer=opt, metrics=["accuracy"])
    #model.summary()
    #model.fit(x=X_train, y=Y_train, epochs=10, batch_size=32, shuffle=True)

    model.fit_generator(
        generator2,
        steps_per_epoch=math.ceil(len(X_train[train])/batch_size),
        epochs=no_epochs,
        #shuffle=True,
        verbose=1,
        #initial_epoch=32,
        validation_data=(X_train[test], Y_train[test]),
        callbacks=[early_stopping, lrs, terminate_on_nan, model_checkpoint, reduce_lr])

    print("FOLD OVER", i)
    i += 1

print("Training Done::Evaluating")
#print(model.evaluate(X_train[test], Y_train[test]))

'''
    STEP 4 : Prepare test samples
'''
X_test = []
for i in range(0, test_samples):
    data = np.load("data/test/test/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, 102))
    zero_mat[:data.shape[0], :] = data
    X_test.append(zero_mat)

X_test = np.array(X_test)

print(X_test.shape)

'''
    STEP 5 : Predict on test
'''
pred = model.predict(X_test)

'''
    STEP 6 : Save data to csv
'''
print(pred.shape, pred)
pred = pd.DataFrame(data=pred, index=[i for i in range(pred.shape[0])], columns=["Predicted"])
pred.to_csv('final_Kfold_v3.csv', index=True)