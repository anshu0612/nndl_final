
import numpy as np
import math
import pandas as pd
from keras.models import Model
from keras.layers import Dense, Activation, Dropout, Input, Multiply, TimeDistributed, LSTM, Conv1D
from keras.layers import Bidirectional, BatchNormalization, Concatenate, GlobalMaxPooling1D
from keras.optimizers import Adam
from keras.callbacks.callbacks import TerminateOnNaN, ModelCheckpoint, LearningRateScheduler, ReduceLROnPlateau

'''
    STEP 1 : Getting training sample
'''
<<<<<<< Updated upstream
train_samples = 18622
=======
samples = 18622
>>>>>>> Stashed changes
# 18622
test_samples = 6051
#6051
batch_size = 256
no_epochs = 30
n_x = 102

# max length of a sequence
max_Tx = 1000
X_train = []

for i in range(0, train_samples):
    data = np.load("data/train/train/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, n_x))
    zero_mat.put(i, data)
    X_train.append(zero_mat)

X_train = np.array(X_train)

# y_4 =  df.loc[df['Id'] == 200, ['Label']]
df = pd.read_csv("data/train_kaggle.csv", usecols=["Label"])
Y_train = df[:train_samples]
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
opt = Adam(learning_rate=0.01, beta_1=0.9, beta_2=0.999, decay=0.01)
model.compile(loss='binary_crossentropy', optimizer=opt, metrics=["accuracy"])
#model.summary()
<<<<<<< Updated upstream
#model.fit(x=X_train, y=Y_train, epochs=10, batch_size=32, shuffle=True)
num_samples = X_train.shape[0]

def generate_data(x_data, y_data, b_size):

    samples_per_epoch = x_data.shape[0]
    number_of_batches = samples_per_epoch/b_size
    counter = 0

    while 1:
        x_batch = np.array(x_data[batch_size*counter:batch_size*(counter+1)]).astype('float32')
        y_batch = np.array(y_data[batch_size*counter:batch_size*(counter+1)]).astype('float32')
        counter += 1
        yield x_batch, y_batch

        if counter >= number_of_batches:
            counter = 0


reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.2, patience=5, min_lr=0.001)
terminate_on_nan = TerminateOnNaN()
model_checkpoint = ModelCheckpoint("checkpoint.txt", monitor='val_loss')
#https://stackoverflow.com/questions/39779710/setting-up-a-learningratescheduler-in-keras
#learning_scheduler = LearningRateScheduler()

model.fit_generator(generate_data(X_train, Y_train, batch_size), steps_per_epoch=math.ceil(num_samples/batch_size), epochs=no_epochs,
                    callbacks=[terminate_on_nan, model_checkpoint, reduce_lr])
=======
model.fit(x=X_train, y=Y_train, batch_size= 256, epochs=40)
>>>>>>> Stashed changes


'''
    STEP 4 : Prepare test samples
'''
<<<<<<< Updated upstream
=======
test_samples = 6051
#6051
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
pred.to_csv('test_v5.csv', index=True)
anshu:=======
pred.to_csv('test_v4.csv',index=True)
>>>>>>> Stashed changes
