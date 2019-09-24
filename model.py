
import numpy as np
import pandas as pd
from keras.models import Model, load_model
from keras.layers import Dense, Activation, Dropout, Input, Multiply, TimeDistributed, LSTM, Conv1D
from keras.layers import Bidirectional, BatchNormalization, Reshape, Concatenate, GlobalMaxPooling1D
from keras.optimizers import Adam
from keras.preprocessing import sequence

import os
# print("##########", os.walk('data/'))
# for dirname, _, filenames in os.walk('data/'):
#      for filename in filenames:
#          print(os.path.join(dirname, filename))

# my_path = os.path.abspath(os.path.dirname(__file__))
# path = os.path.join(my_path, "../data/test.csv")
# with open(path) as f:
#     test = list(csv.reader(f))

'''
    STEP 1 : Getting training sample
'''
samples = 1
# 18622
# number of features
n_x = 102

# max length of a sequence
max_Tx = 1000
X_train = []

for i in range(0, samples):
    data = np.load("data/train/train/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, n_x))
    zero_mat.put(i, data)
    X_train.append(zero_mat)

X_train = np.array(X_train)

# y_4 =  df.loc[df['Id'] == 200, ['Label']]
df = pd.read_csv("data/train_kaggle.csv", usecols=["Label"])
Y_train = df[:samples]
# usecols=["Label"]

print(X_train.shape, Y_train.shape)


'''
    STEP 2 : model
'''
def malware_detection_model(input_shape):
    X_input = Input(shape=input_shape)

    # Normalization 1
    X = BatchNormalization()(X_input)
    a = X
    b = X

    # Gated CNN 1
    a = Conv1D(filters=128, kernel_size=2, strides=1)(a)
    a_sig = Activation('sigmoid')(a)
    a = Multiply()([a, a_sig])

    # Gated CNN 2
    b = Conv1D(filters=128, kernel_size=3, strides=1)(b)
    b_sig = Activation('sigmoid')(b)
    b = Multiply()([b, b_sig])

    # Concatenate
    X = Concatenate(axis=1)([a, b])

    # Normalization 2
    X = BatchNormalization()(X)

    # BidirectionalLSTM
    X = Bidirectional(LSTM(100, return_sequences=True))(X)

    X = GlobalMaxPooling1D()(X)

    X = Dense(64, activation='relu')(X)

    X = Dropout(0.5)(X)

    X = Dense(1, activation='sigmoid')(X)

    model = Model(inputs=X_input, outputs=X)

    return model

'''
    STEP 3 : Train model
'''
model = malware_detection_model(input_shape = (max_Tx, n_x))
opt = Adam(lr=0.0001, beta_1=0.9)
model.compile(loss='binary_crossentropy', optimizer=opt, metrics=["accuracy"])
#model.summary()
model.fit(x=X_train, y=Y_train, epochs=1)


'''
    STEP 4 : Prepare test samples
'''
test_samples =
#6051
X_test = []
for i in range(0, test_samples):
    data = np.load("data/test/test/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, n_x))
    zero_mat.put(i, data)
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
pred.to_csv('test_v3.csv',index=True)