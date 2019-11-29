from argparse import ArgumentParser
import json
from os.path import dirname, isfile

def load_config():
    path_to_config_file = f'{dirname(__file__)}/default_config.json'

    with open(path_to_config_file, 'r') as config:
        return json.loads(config.read())

    return None

def parse_argument():
    parser = ArgumentParser()

    parser.add_argument("-bs", "--batch-size", dest="batch_size",
                        help="Usage constant of batch size")
    parser.add_argument("-lr", "--learning-rate", dest="learning_rate",
                        help="Usage constant of learning rate")
    parser.add_argument("-e", "--epochs", dest="num_epochs",
                        help="Usage of number of epochs")
    parser.add_argument("-v", "--verbose", dest="verbose",
                        help="Usage of loss verbose")

    return parser.parse_args()

def get_merged_values():
    config = load_config()
    argvs = vars(parse_argument())

    for attr, value in config.items():
        if argvs[attr] is not None:
            config[attr] = argvs[attr]

    return config


