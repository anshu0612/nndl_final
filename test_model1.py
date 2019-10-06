import numpy as np
import math
import pandas as pd
from sklearn.model_selection import train_test_split
from keras.callbacks.callbacks import TerminateOnNaN, ModelCheckpoint, LearningRateScheduler, ReduceLROnPlateau, \
    EarlyStopping
from model1 import malware_detection_model_1

'''
    STEP 1 : Getting training sample
'''
train_samples = 18622
# 18622
test_samples = 6051
# 6051
batch_size = 128
no_epochs = 20
n_x = 102

# max length of a sequence
max_Tx = 1000
X_t = []

for i in range(0, train_samples):
    data = np.load("data/train/train/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, 102))
    zero_mat[:data.shape[0], :] = data
    X_t.append(zero_mat)

X_t = np.array(X_t)
df = pd.read_csv("data/train_kaggle.csv", usecols=["Label"])
Y_t = df[:train_samples]
Y_t = Y_t.values

print(X_t.shape, Y_t.shape)

X_train, X_val, Y_train, Y_val = train_test_split(X_t, Y_t, test_size=0.20)

'''
    STEP 3 : Train model
'''
num_samples = X_train.shape[0]


def step_decay(epoch):
    if 13 <= epoch <= 20:
        print("LR is 0.001")
        return 0.001
    elif epoch > 20:
        print("LR is 0.0001")
        return 0.0001
    print("LR is 0.01")
    return 0.01

lrate = LearningRateScheduler(step_decay)


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


generator2 = generate_data(X_train, Y_train, batch_size)

reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=5, verbose=1, mode='min')
terminate_on_nan = TerminateOnNaN()
model_checkpoint = ModelCheckpoint("test_model1_cp", monitor='loss', save_best_only=True, mode='min')
early_stopping = EarlyStopping(monitor='loss', patience=5, mode='auto')

momentum = 0.8
model = malware_detection_model_1()
model.fit_generator(
    generator2,
    steps_per_epoch=math.ceil(len(X_train) / batch_size),
    epochs=no_epochs,
    shuffle=True,
    verbose=1,
    #initial_epoch=36,
    validation_data=(X_val, Y_val),
    callbacks=[early_stopping, terminate_on_nan, reduce_lr, model_checkpoint])

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
print("result", pred)
'''
    STEP 6 : Save data to csv
'''
# Dump predictions into submission file
pred = pd.DataFrame(data=pred, index=[i for i in range(pred.shape[0])], columns=["Predicted"])
pred.index.name = 'Id'
pred.to_csv('test_model1.csv', index=True)
