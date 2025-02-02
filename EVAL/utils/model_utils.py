import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.utils import plot_model
from tensorflow.keras.applications.vgg16 import VGG16

from keras_custom.models.language_model import lang_model, lang_model_contrastive


"""
Some pre-defined models that are used repeatedly.
"""

def ready_model(config, lossW, return_semantic=True):
    """
    Load in a specified simclr model and intercept activation after the
    semantic layer.
    """
    model = lang_model_contrastive(config, return_semantic=return_semantic)

    print(f'[Check] front_end=', config['front_end'])
    if config['front_end'] == 'simclr':
        if config['headless'] is True:
            model.build(input_shape=(1, 2048))
        else:
            model.build(input_shape=(1,224,224,3))
    elif config['front_end'] == 'vgg16':
        pass  # nothing needs done.
    
    w2_depth = config['w2_depth']
    config_version = config['config_version']

    # only to produce output at semantic layer.
    # so we load weights only until semantic layer.
    for i in range(w2_depth):
        with open(f'_trained_weights/{config_version}/w2_dense_{i}-{config_version}-lossW={lossW}.pkl', 'rb') as f:
            dense_weights = pickle.load(f)
            model.get_layer(f'w2_dense_{i}').set_weights([dense_weights[0], dense_weights[1]])
            print(f'Successfully loading layer weights for [w2_dense_{i}]')

    with open(f'_trained_weights/{config_version}/semantic_weights-{config_version}-lossW={lossW}.pkl', 'rb') as f:
        semantic_weights = pickle.load(f)
        model.get_layer('semantic_layer').set_weights([semantic_weights[0], semantic_weights[1]])
        print(f'Successfully loading layer weights for [semantic]')
    # load all trained weights including the final discrete layer.
    if return_semantic is True:
        return model
    else:
        with open(f'_trained_weights/{config_version}/discrete_weights-{config_version}-lossW={lossW}.pkl', 'rb') as f:
            discrete_weights = pickle.load(f)
            model.get_layer('discrete_layer').set_weights([discrete_weights[0], discrete_weights[1]])
            print(f'Loaded layer weights for [discrete]')
        return model


def ready_model_for_ind_accuracy_eval(w2_depth, run_name, lossW):
    """
    Reconstruct the model for evaluating individual 
    class accuracies.

    One important change to the model for evaluating distances
    is that the semantic output will be removed and the model is 
    back to be a classification only model.

    Reason we perform this remove step is because, if we keep
    semantic output, we have to use the word2vec matrix trick from
    Nick. The result of that is we cannot evaluate individual classes
    but all 1000 classes at once, which isn't what we want.

    Also, this script applies to both regular training and superordinate
    training models.
    """
    # model structure at training
    model = lang_model(w2_depth=w2_depth)

    # for eval accuracy, the semantic output is not needed.
    model = Model(inputs=model.input, outputs=model.output[1])

    # load trained weights
    ## w2 dense weights
    for i in range(w2_depth):
        with open(f'_trained_weights/w2_dense_{i}-{run_name}.pkl', 'rb') as f:
            dense_weights = pickle.load(f)
            model.get_layer(f'w2_dense_{i}').set_weights([dense_weights[0], dense_weights[1]])
            print(f'Successfully loading layer weights for [w2_dense_{i}]')

    ## semantic weights
    with open(f'_trained_weights/semantic_weights-{run_name}.pkl', 'rb') as f:
        semantic_weights = pickle.load(f)
        model.get_layer('semantic').set_weights([semantic_weights[0], semantic_weights[1]])
        print(f'Successfully loading layer weights for [semantic]')

    with open(f'_trained_weights/discrete_weights-{run_name}.pkl', 'rb') as f:
        discrete_weights = pickle.load(f)
        model.get_layer('discrete').set_weights([discrete_weights[0], discrete_weights[1]])
        print(f'Successfully loading layer weights for [discrete]')

    model.compile(tf.keras.optimizers.Adam(lr=3e-5),
                  loss=['sparse_categorical_crossentropy'],
                  metrics=['acc', 'top_k_categorical_accuracy'])

    print(f'run_name: {run_name}')
    return model


def vgg16_intersected_model(layer='block4_pool'):
    """
    intersected VGG16 at a given layer output
    """
    model = VGG16(weights='imagenet', include_top=True, input_shape=(224, 224, 3))
    intersected_output = model.get_layer(layer).output
    model = Model(inputs=model.input, outputs=intersected_output)

    model.compile(tf.keras.optimizers.Adam(lr=3e-5),
                  loss=['categorical_crossentropy'])

    print(f'loading VGG16 model until layer = {layer}')
    return model