import numpy as np
import math
import pandas as pd
from keras.callbacks.callbacks import TerminateOnNaN, ModelCheckpoint, ReduceLROnPlateau,\
    EarlyStopping
from sklearn.model_selection import StratifiedKFold

from model1 import malware_detection_model_1
from model2 import malware_detection_model_2
from model3 import malware_detection_model_3
from model4 import malware_detection_model_4

train_samples = 18622
test_samples = 6051
batch_sizes = [32, 64, 128]
no_epochs = 100
# number of features
n_x = 102
# max length of a sequence
max_Tx = 1000
X_t = []

'''
    STEP 1 : Getting training sample
'''
# Training Data Pre-processing: padding sequences with 0
for i in range(0, train_samples):
    data = np.load("data/train/train/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, 102))
    zero_mat[:data.shape[0], :] = data
    X_t.append(zero_mat)

X_train = np.array(X_t)
df = pd.read_csv("data/train_kaggle.csv", usecols=["Label"])
Y_t = df[:train_samples]
Y_train = Y_t.values

'''
    STEP 2 : Prepare test samples
'''
X_test = []
# Testing Data Pre-processing: padding sequences with 0
for i in range(0, test_samples):
    data = np.load("data/test/test/" + str(i) + ".npy")
    zero_mat = np.zeros((max_Tx, 102))
    zero_mat[:data.shape[0], :] = data
    X_test.append(zero_mat)
X_test = np.array(X_test)

'''
    STEP 3 : Add models for ensembling
'''

models = list()
models.append(malware_detection_model_1)
models.append(malware_detection_model_2)
models.append(malware_detection_model_3)
models.append(malware_detection_model_4)


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

'''
    STEP 4 : Train each of the 4 models over different batch size of 32, 64 and 128
'''
output_labels = []
for m in range(len(models)):
    for batch_size in batch_sizes:
        fold_no = 1
        labels = []
        for train, test in kfolds.split(X_train, Y_train):
            print("Model No.", m + 1, 'for batch size', batch_size, "and fold no.", fold_no)
            data_generator = generate_data(X_train[train], Y_train[train], batch_size)
            reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=4, verbose=1, mode='min')
            terminate_on_nan = TerminateOnNaN()
            # model_checkpoint = ModelCheckpoint("ch", monitor='loss', save_best_only=True, mode='min')
            early_stopping = EarlyStopping(monitor='val_accuracy', patience=4, mode='auto')
            model = models[m]()
            history = model.fit_generator(
                data_generator,
                steps_per_epoch=math.ceil(len(X_train[train]) / batch_size),
                epochs=no_epochs,
                shuffle=True,
                verbose=1,
                # initial_epoch=9,
                validation_data=(X_train[test], Y_train[test]),
                callbacks=[early_stopping, terminate_on_nan, reduce_lr])

            # predict
            pred = model.predict(X_test)
            # If the model has last layer as Softmax (model 4), take probabilities of 1
            pred = pred if m != 3 else pred[:, 1].reshape(test_samples, 1)
            labels.append(pred)
            fold_no += 1

        labels = np.array(labels)
        labels = np.mean(labels, axis=0)
        output_labels.append(labels)

output_labels = np.array(output_labels)
output_labels = np.mean(output_labels, axis=0)
'''
    STEP 6 : Save data to csv
'''
# Dump predictions into submission file
final_pred = pd.DataFrame(data=output_labels,
                          index=[i for i in range(output_labels.shape[0])],
                          columns=["Predicted"])
final_pred.index.name = 'Id'
final_pred.to_csv('output.csv', index=True)
