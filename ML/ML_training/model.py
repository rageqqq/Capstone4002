#model.py
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import adam_v2
import numpy as np
from features import extract_features
import pandas as pd

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sn

def prepare_training_data(segments, labels):
    """Prepares data in the correct format for training

        Extracts features for each of the samples and prepares the labels in one hot encoding

        Args:
            segments (list): list of samples
            labels(list): list of string labels
        
        Returns:
            extracted (list): flattened lists of ml training data inputs
            one_hot (list): one hot encoded list of labels
        """
    
    extracted = extract_features(segments)
    one_hot = np.asarray(pd.get_dummies(labels), dtype = np.float32)
    return (extracted, one_hot)


def model_eval(model, X_test, y_test):
    """Evaluates the trained model

        checks the test accuracy and loss and displays a confusion matrix

        Args:
            model (keras model): trained ml model
            X_test(list): list of test inputs
            y_test(list): list of one hot encoded expected outputs
        
        """

    loss, acc = model.evaluate(x=X_test, y=y_test)
    y_prediction = model.predict(X_test)
    print("Test accuracy: %3.2f, loss: %3.2f"%(acc, loss))

    y_pred=np.argmax(y_prediction, axis=1)
    y_test=np.argmax(y_test, axis=1)
    cm = confusion_matrix(y_test, y_pred)

    df_cm = pd.DataFrame(cm, range(4), range(4))
    plt.figure(figsize=(10,7))
    sn.set(font_scale=1.4) # for label size
    sn.heatmap(df_cm, annot=True, annot_kws={"size": 16}, fmt='g') # font size

    plt.show()

    #np.savetxt('x.csv', X_test, delimiter=',')
    #np.savetxt('y.csv', y_test, delimiter=',')



def np_to_cpp(data):
    """Prepares data in the correct format for HLS array

        converts transposed np array to c array format in string

        Args:
            data (np array): np.array to convert to cpp array
        
        Returns:
            String: np array data in c array format

            
        """
    layer = np.transpose(np.array(data))
    layer_flat = layer.flatten()
    layer_cpp = '{'
    for i in range(len(layer_flat)):
        layer_cpp += str(layer_flat[i])
        if i < len(layer_flat)-1:
            layer_cpp +=','
    layer_cpp +='}'
    return layer_cpp

def bias_to_cpp(data):
    """Prepares data in the correct format for HLS array

        converts np array to c array format in string

        Args:
            data (np array): np.array to convert to cpp array
        
        Returns:
            String: np array data in c array format

            
        """

    layer = np.array(data)
    layer_flat = layer.flatten()
    layer_cpp = '{'
    for i in range(len(layer_flat)):
        layer_cpp += str(layer_flat[i])
        if i < len(layer_flat)-1:
            layer_cpp +=','
    layer_cpp +='}'
    return layer_cpp


def model_to_cpp(model):
    """Prepares trained model in the correct format for HLS

        converts keras model to HLS format in string

        Args:
            model (keras model): model to extract into HLS code
        
        Returns:
            String: model and weights in HLS usable code

            
        """


    layer_1_cpp = np_to_cpp(model.layers[0].get_weights()[0])
    layer_1_bias = bias_to_cpp(model.layers[0].get_weights()[1])
    layer_2_cpp = np_to_cpp(model.layers[1].get_weights()[0])
    layer_2_bias = bias_to_cpp(model.layers[1].get_weights()[1])
    layer_3_cpp = np_to_cpp(model.layers[2].get_weights()[0])
    layer_3_bias = bias_to_cpp(model.layers[2].get_weights()[1])
    w_1 = "float l1_weight[INPUT_LAYER * LAYER_1] = " + layer_1_cpp
    w_2 = "float l2_weight[LAYER_1 * LAYER_2] = " + layer_2_cpp
    w_3 = "float output_weight[LAYER_2 * OUTPUT_LAYER] = " + layer_3_cpp
    b_1 = "float l1_bias[LAYER_1] = " + layer_1_bias
    b_2 = "float l2_bias[LAYER_2] = " + layer_2_bias
    b_3 = "float output_bias[OUTPUT_LAYER] = " + layer_3_bias

    file = open("cpp_weights.txt", "a+")
    file.write(w_1)
    file.write("\n")
    file.write("\n")
    file.write(w_2)
    file.write("\n")
    file.write("\n")
    file.write(w_3)
    file.write("\n")
    file.write("\n")
    file.write(b_1)
    file.write("\n")
    file.write("\n")
    file.write(b_2)
    file.write("\n")
    file.write("\n")
    file.write(b_3)

  