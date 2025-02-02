import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import argparse
from EVAL import compute_activations_n_matrices
from EVAL.utils.data_utils import load_config
from EVAL import check_trained_simclr_acc
from EVAL import results_vis


def str2bool(v):
    """
    Purpose:
    --------
        Such that parser returns boolean as input to function.
    """
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser()
parser.add_argument('-l', '--label', dest='label')
parser.add_argument('-f', '--frontend', dest='frontend')
parser.add_argument('-v', '--version', dest='version')
parser.add_argument('-s', '--semantics', dest='semantics', type=str2bool)
parser.add_argument('-m', '--matrices', dest='matrices', type=str2bool)
parser.add_argument('-a', '--accuracy', dest='accuracy', type=str2bool)
parser.add_argument('-p', '--plot', dest='plot', type=str2bool)
parser.add_argument('-gpu', '--gpu', dest='gpu_index')
args = parser.parse_args()

'''
Example command:
    python main_eval.py -l finegrain -f simclr -v v3.1.run12 -s True -m True -gpu 0
'''

if __name__ == '__main__':
    
    os.environ["CUDA_VISIBLE_DEVICES"]= f'{args.gpu_index}'

    config_version = f'{args.frontend}_{args.label}_{args.version}'
    config = load_config(config_version)

    if args.semantics is not None:
        print(f'**** Computing intermediate results for plotting ****')
        whether_compute_semantics = args.semantics
        whether_compute_matrices = args.matrices
        compute_activations_n_matrices.execute(config=config, 
                                            compute_semantic_activation=whether_compute_semantics,
                                            compute_distance_matrices=whether_compute_matrices)
    elif args.accuracy is True:
        print(f'**** Computing trained model accuracy ****')
        check_trained_simclr_acc.execute(config)
    
    elif args.plot is True:
        print(f'**** Plotting all final results ****')
        results_vis.execute(config)