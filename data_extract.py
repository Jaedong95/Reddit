'''
2010~2016 rc, rs data -> sentence split 
'''
import pandas as pd 
import json
import os 
import argparse 
from attrdict import AttrDict
from src import Zstd, RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path, args.year) 
    zstd = Zstd()
    reddit = RedditData(args.subreddit, data_path)
    rs = reddit.extract_subreddit(args.year, 'RS', zstd)
    rc = reddit.extract_subreddit(args.year, 'RC', zstd)
    rs_df = reddit.convert_df(rs)
    rc_df = reddit.convert_df(rc)
    save_dir = os.path.join(default_path, 'data', 'origin') 
    reddit.save_df(rs_df, os.path.join(save_dir, args.year + '_rs.csv'))
    reddit.save_df(rc_df, os.path.join(save_dir, args.year + '_rc.csv'))
    print(len(rs), len(rc))
    print(len(rs_df), len(rc_df))
    

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have reddit data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')

    cli_argse = cli_parser.parse_args()
    main(cli_argse) 