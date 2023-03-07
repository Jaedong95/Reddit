import pandas as pd 
import json
import os 
import argparse 
from attrdict import AttrDict
from src import RedditData, RedditProcessor

def main(args):
    with open(os.path.join(args.config_path, args.config_file)) as f:
        data_config = AttrDict(json.load(f))

    data_config.default_path = os.getcwd()
    data_config.data_path = os.path.join(data_config.default_path, args.data_path)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    
    

    cli_argse = cli_parser.parse_args()
    main(cli_argse)