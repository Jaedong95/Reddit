import pandas as pd 
import os 
import argparse 
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

    reddit_df = pd.concat([rs_title, rs_selftext, rc_body]) 

    ''' data pre-process ''' 
    print(f'data length before pre-process.. {len(reddit_df)}')

    reddit_df = reddit_p.drop_na(reddit_df)   # drop na 
    reddit_df = reddit_p.drop_odd('text', reddit_df)   # drop cross post, deleted data 
    reddit_df.text = reddit_df.text.apply(reddit_p.cleanse_text)
    reddit_df = reddit_p.drop_duplicates('text', reddit_df)
    reddit_df = reddit_p.map_rc_rs(reddit_df)
    
    print(f'data length after pre-process.. {len(reddit_df)}')
    reddit.save_df(reddit_df, os.path.join(save_dir, 'dataset1_' + args.year + '.csv'))

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)