import pandas as pd
import re 
import os 
import argparse 
from src import RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    
    # load class 
    reddit = RedditData(args.subreddit, data_path)
    reddit_p = RedditProcessor(args.data_path)

    # reddit = pd.read_csv(os.path.join(data_path, 'origin', f'{args.year}_rc.csv'))
    reddit = pd.read_csv(os.path.join(data_path, 'processed', 'aud_dsm.csv'))
    print(reddit.head(1))
    tramadol = reddit[reddit['link_id'] == 't3_akj8u']
    
    lebalove = tramadol[tramadol['author'] == 'lebalove']
    nico3d3 = tramadol[tramadol['author'] == 'Nico3d3']
    # sarahC = tramadol[tramadol['author'] == 'SarahC']
    wally = tramadol[tramadol['author'] == 'wallythecat']
    print(nico3d3[['link_id', 'author', 'parent_id', 'body', 'name']], end='\n\n')
    print(wally[['link_id', 'author', 'parent_id', 'body', 'name']], end='\n\n')
    print(lebalove[['link_id', 'author', 'parent_id', 'body', 'name']])


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)