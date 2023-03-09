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

    ''' data pre-process ''' 
    print(f'data length before pre-process.. rs: {len(rs_df)}, rc: {len(rc_df)}')
    
    # drop na 
    rs_df = reddit_p.drop_na(rs_df)
    rc_df = reddit_p.drop_na(rc_df)
    
    # drop cross post, deleted data 
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
    print(f'data length after pre-process.. rs: {len(rs_df)}, rc: {len(rc_df)}')

    ''' save dataset1.csv '''
    rs_title = rs_df.copy()
    rs_title = rs_title[['id', 'subreddit', 'title']]
    rs_title.columns = ['id', 'subreddit', 'text']
    rs_title['type'] = 'title'
    
    rs_selftext = rs_df.copy()
    rs_selftext = rs_selftext[['id', 'subreddit', 'selftext']]
    rs_selftext.columns = ['id', 'subreddit', 'text'] 
    rs_selftext['type'] = 'post'
    
    rc_body = rc_df.copy() 
    rc_body.columns = ['id', 'subreddit', 'body']
    rc_body.columns = ['id', 'subreddit', 'text']
    rc_body['type'] = 'comment'

    reddit_df = pd.concat([rs_selftext, rs_title, rc_body]) 
    reddit.save_df(reddit_df, os.path.join(save_dir, 'dataset1_' + args.year + '.csv'))

    ''' data pre-process2  - to create dataset2.csv ''' 
    # split sentence 

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)