'''
2010~2016 rc, rs data -> sentence split 
'''
import pandas as pd 
import json
import os 
import argparse 
from attrdict import AttrDict
from src import RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path, args.year)
    subreddit = args.subreddit 
    reddit = RedditData(subreddit, data_path)
    rs, _ = reddit.extract_info(args.year, 'rs')
    rc, _ = reddit.extract_info(args.year, 'rc')
    

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have reddit data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')

    cli_argse = cli_parser.parse_args()
    main(cli_argse) 