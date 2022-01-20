# import tensorflow as tf
# print(tf.__version__)

# import keras
# print(keras.__version__)

from tensorflow.python.keras.applications.vgg16 import VGG16
from tensorflow.python.keras.preprocessing.image import load_img
from tensorflow.python.keras.preprocessing.image import img_to_array
from tensorflow.python.keras.applications.vgg16 import preprocess_input
import numpy as np
from tensorflow.python.keras.applications.vgg16 import decode_predictions

# call VGG16 model
model = VGG16()


def vgg(pass_of_image, model):
    # call VGG16 model
    # model = VGG16()

    # resize image to 224 x 224 which is a size of VGG16's input
    img = load_img(pass_of_image, target_size=(224, 224))

    # PIL_Image(?) -> numpy.ndarray
    img_arr = img_to_array(img)

    # convert to VGG16 model's image at the time of prior learning(?)
    img_for_vgg = preprocess_input(img_arr)

    img_input = np.stack([img_for_vgg])

    # confirm shape of input data
    # print('shape of arr_input:', arr_input.shape)

    # calculate probability
    probability = model.predict(img_input)

    # confirm shape of probability
    # print('shape of probs:', probs.shape)

    # print(probability)

    results = decode_predictions(probability)

    return results[0]
