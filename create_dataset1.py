import pandas as pd 
import os 
import argparse 
from src import RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    save_path = os.path.join(data_path, 'processed')

    reddit = RedditData(args.subreddit, data_path)
    reddit_p = RedditProcessor(args.data_path)

    # load data 
    rs_df = reddit.load_df(os.path.join(data_path, 'origin', args.year + '_rs.csv'))
    rc_df = reddit.load_df(os.path.join(data_path, 'origin', args.year + '_rc.csv'))
    
    # rs: id, subreddit, title, selftext
    rs_col = ['id', 'subreddit', 'author', 'title', 'selftext', 'created_utc']
    rs_df = rs_df[rs_col]
    rs_df['parent_id'] = rs_df['id']
    rs_df['o_id'] = rs_df['id']

    # rc: link_id, subreddit, body 
    rc_col = ['link_id', 'subreddit', 'author', 'body', 'created_utc', 'parent_id', 'id']
    rc_df = rc_df[rc_col]

    rs_title = rs_df.copy()   
    rs_title = rs_title[['id', 'subreddit', 'author', 'title', 'created_utc', 'parent_id', 'o_id']]
    rs_title.columns = ['id', 'subreddit', 'author', 'text', 'time', 'parent_id', 'o_id']
    rs_title['type'] = 'title'
    
    rs_selftext = rs_df.copy()
    rs_selftext = rs_selftext[['id', 'subreddit', 'author', 'selftext', 'created_utc', 'parent_id', 'o_id']]
    rs_selftext.columns = ['id', 'subreddit', 'author', 'text', 'time', 'parent_id', 'o_id'] 
    rs_selftext['type'] = 'post'
    
    rc_body = rc_df.copy() 
    rc_body.columns = ['id', 'subreddit', 'author', 'text', 'time', 'parent_id', 'o_id']
    rc_body['type'] = 'comment'

    reddit_df = pd.concat([rs_title, rs_selftext, rc_body]) 
    reddit_df.reset_index(inplace=True, drop=True) 

    ''' data pre-process ''' 
    print(f'data length before pre-process.. {len(reddit_df)}')
    
    tok_list = ['', 0, ' ', '.', '..', '...']
    reddit_df = reddit_p.drop_na(reddit_df, type=1, col='text', tok_list=tok_list)
    # reddit_df = reddit_p.drop_na(reddit_df)   # drop na 
    reddit_df = reddit_p.drop_odd('text', reddit_df)   # drop cross post, deleted data 
    reddit_df.text = reddit_df.text.apply(reddit_p.cleanse_text)   # cleanse text 
    reddit_df = reddit_p.drop_duplicates('text', reddit_df)   # drop duplicates 
    reddit_df = reddit_p.drop_na(reddit_df)
    # reddit_df = reddit_p.map_rc_rs(reddit_df)    # delete comment that does not have parent post 
    
    print(f'data length after pre-process.. {len(reddit_df)}')
    # reddit.save_df(reddit_df, os.path.join(save_path, 'dataset1_' + args.year + '.csv'))
    reddit.save_df(reddit_df, os.path.join(save_path, 'dataset1_' + args.year + '.csv'))

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)