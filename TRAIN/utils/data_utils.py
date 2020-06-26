import numpy as np
import pandas as pd
import socket


def load_classes(num_classes, df='imagenetA'):
    """
    load in all imagenet/imagenetA or other dataframe classes,
    return:
    -------
        n classes of wnids, indices and descriptions
    """
    df = pd.read_csv(f'groupings-csv/{df}_Imagenet.csv',
                     usecols=['wnid', 'idx', 'description'])
    sorted_indices = np.argsort([i for i in df['wnid']])[:num_classes]

    wnids = np.array([i for i in df['wnid']])[sorted_indices]
    indices = np.array([int(i) for i in df['idx']])[sorted_indices]
    descriptions = np.array([i for i in df['description']])[sorted_indices]
    return wnids.tolist(), indices, descriptions


def data_directory(subset):
    """
    Check which server we are on and return the corresponding 
    imagenet data directory.
    """
    hostname = socket.gethostname()
    server_num = int(hostname[4:6])
    print(f'server_num = {server_num}')
    if server_num <= 20:
        imagenet_dir = f'/mnt/fast-data{server_num}/datasets/ILSVRC/2012/clsloc/{subset}/'
    else:
        imagenet_dir = f'/fast-data{server_num}/datasets/ILSVRC/2012/clsloc/{subset}/'
    return imagenet_dir