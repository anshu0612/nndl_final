import numpy as np
import math
import pandas as pd
from keras.callbacks.callbacks import TerminateOnNaN, ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from sklearn.model_selection import StratifiedKFold
from keras.models import load_model

from model3 import malware_detection_model_3
# SGD
from model4 import malware_detection_model_4
# softmax
from model5 import malware_detection_model_5
# 64X64
from model6 import malware_detection_model_6

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
X_t = []

for i in range(0, train_samples):
    data = np.load("data/train/train/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, 102))
    zero_mat[:data.shape[0], :] = data
    X_t.append(zero_mat)

X_train = np.array(X_t)
df = pd.read_csv("data/train_kaggle.csv", usecols=["Label"])
Y_t = df[:train_samples]
Y_train = Y_t.values

print(X_train.shape, Y_train.shape)
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
print("X_test", X_test.shape)
'''
    STEP 3 : Train model
'''

models = []
# models.append(malware_detection_model_5())
# models.append(malware_detection_model_3())
# models.append(malware_detection_model_6())
# models.append(malware_detection_model_3())

# load from checkpoints
models.append(load_model("cp_bk/test_model1_softmax_cp"))
models.append(load_model("cp_bk/test_model1_kf_cp"))
models.append(load_model("cp_bk/test_model6_kf_cp"))


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

kfolds = StratifiedKFold(n_splits=4,  shuffle=True, random_state=1)

final_labels = []
for m in range(len(models)):
    print("MODEL NO.:", m + 1)
    f = 1
    labels = []
    for train, test in kfolds.split(X_train, Y_train):
        print("FOLD no:", f)
        generator2 = generate_data(X_train, Y_train, batch_size)
        reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=5, verbose=1, mode='min')
        terminate_on_nan = TerminateOnNaN()
        model_checkpoint = ModelCheckpoint("final_v1_cp", monitor='loss', save_best_only=True, mode='min')
        early_stopping = EarlyStopping(monitor='loss', patience=4, mode='auto')

        models[m].fit_generator(
            generator2,
            steps_per_epoch=math.ceil(len(X_train) / batch_size),
            epochs=no_epochs,
            shuffle=True,
            verbose=1,
            initial_epoch=9,
            validation_data=(X_train[test], Y_train[test]),
            callbacks=[early_stopping, terminate_on_nan, reduce_lr, model_checkpoint])

        #predict
        pred = models[m].predict(X_test)
        pred = pred if m != 0 else pred[:, 1].reshape(test_samples, 1)
        print(pred.shape, pred)
        labels.append(pred)

        df = pd.DataFrame(data=pred)
        df.to_csv('model' + str(m) + '.csv', index=True)

        f += 1

    labels = np.array(labels)
    print("K fold done for model", m, "shape is", labels.shape)
    labels = np.mean(labels, axis=0)
    final_labels.append(labels)

final_labels = np.array(final_labels)
print("Ensemble labels shape:", final_labels.shape)
final_labels = np.mean(final_labels, axis=0)

print("LABLES", final_labels)
'''
    STEP 6 : Save data to csv
'''
# Dump predictions into submission file
final_pred = pd.DataFrame(data=final_labels, index=[i for i in range(final_labels.shape[0])], columns=["Predicted"])
final_pred.index.name = 'Id'
final_pred.to_csv('kf_ensemble.csv', index=True)
