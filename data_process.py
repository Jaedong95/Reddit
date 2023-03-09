import pandas as pd 
import json
import os 
import argparse 
from attrdict import AttrDict
from src import RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    save_path = os.path.join(args.data_path, 'processed')
    reddit = RedditData(args.subreddit, data_path)
    rs_df = reddit.load_df(os.path.join(data_path, 'origin', args.year + '_rs.csv'))
    rc_df = reddit.load_df(os.path.join(data_path, 'origin', args.year + '_rc.csv'))
    reddit_p = RedditProcessor(args.data_path, save_path)
    save_dir = os.path.join(default_path, 'data', 'processed') 
    
    # rs: id, subreddit, title, selftext
    rs_col = ['id', 'subreddit', 'title', 'selftext']
    rs_df = rs_df[rs_col]

    # rc: link_id, subreddit, body 
    rc_col = ['link_id', 'subreddit', 'body']
    rc_df = rc_df[rc_col]

    '''
    Data process
    1. drop na, cross post, deleted data  
    2. map rs, rc file (use id, link_id)
    3. clean text   -> dataset1.csv 
    4. sentence split 
    5. set max tokens 
    6. clean text 
    7. drop na 
    '''
    # drop na 
    rs_df = reddit_p.drop_na(rs_df)
    rc_df = reddit_p.drop_na(rc_df)
    
    # drop cross post, deleted data 
    print(len(rs_df), len(rc_df))
    rs_df = reddit_p.drop_odd('selftext', rs_df)
    rs_df = reddit_p.drop_odd('title', rs_df)
    rc_df = reddit_p.drop_odd('body', rc_df) 

    # cleanse text 
    rs_df.selftext = rs_df.selftext.apply(reddit_p.cleanse_text)
    rs_df.title = rs_df.title.apply(reddit_p.cleanse_text)
    rc_df.body = rc_df.body.apply(reddit_p.cleanse_text)
    rc_df = reddit_p.map_rc_rs(rs_df, rc_df)
    
    # drop duplicates 
    rs_df = reddit_p.drop_duplicates('selftext', rs_df)
    rs_df = reddit_p.drop_duplicates('title', rs_df)
    rc_df = reddit_p.drop_duplicates('body', rc_df)

    print(len(rs_df), len(rc_df))
    reddit.save_df(rs_df, os.path.join(save_dir, 'dataset1_' + args.year + '_rs.csv'))
    reddit.save_df(rc_df, os.path.join(save_dir, 'dataset1_' + args.year + '_rc.csv'))

    


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)