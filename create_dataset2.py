import pandas as pd
import numpy as np 
import os 
import argparse 
from src import RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    save_path = os.path.join(args.data_path, 'processed')
    reddit = RedditData(args.subreddit, data_path)
    reddit_p = RedditProcessor(args.data_path, save_path)
    save_dir = os.path.join(default_path, 'data', 'processed') 

    reddit_df = reddit.load_df(os.path.join(save_dir, 'dataset1_' + args.year + '.csv'))
    reddit_df = reddit_p.drop_na(reddit_df)

    # convert dataframe 
    reddit_post = reddit_p.convert_df(reddit_df, 'post')
    reddit_title = reddit_p.convert_df(reddit_df, 'title')
    reddit_comment = reddit_p.convert_df(reddit_df, 'comment')
    reddit_df2 = pd.concat([reddit_post, reddit_title, reddit_comment])

    ''' data pre-process2  - to create dataset2.csv ''' 
    print(f'data length before pre-process.. {len(reddit_df2)}')

    reddit_df2.reset_index(inplace=True, drop=True) 
    reddit_df2.text = reddit_df2.text.apply(reddit_p.cleanse_text)
    reddit_df2 = reddit_p.drop_na(reddit_df2)
    reddit_df2 = reddit_p.drop_duplicates('text', reddit_df2)
    reddit_df2 = reddit_p.set_max_tok(reddit_df2, 32)

    print(f'data length after pre-process.. {len(reddit_df2)}')
    reddit.save_df(reddit_df2, os.path.join(save_dir, 'dataset2_' + args.year + '.csv'))

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)