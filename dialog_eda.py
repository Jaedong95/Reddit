import pandas as pd
import re 
import os 
import argparse 
from src import RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    save_path = os.path.join(args.data_path, 'processed')
    
    # load class 
    reddit = RedditData(args.subreddit, data_path)
    reddit_p = RedditProcessor(args.data_path)
    reddit_df = reddit.load_df(os.path.join(save_path, 'document_' + args.year + '.csv'))
    
    # print(reddit_df)
    reddit_df = reddit_p.drop_na(reddit_df)   # 결측값 제거
    author_df = reddit_df[reddit_df.author!='[deleted]']
    author_df = reddit_p.map_rc_rs(author_df) 

    # print(author_df)
    author_title = author_df[author_df.type=='title']
    author_comment = author_df[author_df.type=='comment']
    
    # print(len(author_title), len(author_comment))
    title_id = author_title.id.unique().tolist()
    title_id = ['t3_' + id for id in title_id]
    
    # print(len(title_id))
    dialog_comment = author_comment[author_comment.id.isin(title_id)]
    dialog_comment.reset_index(inplace=True, drop=True)
    
    # print(comments.id.values)
    title_id2 = [id.split('_')[1] for id in title_id if id in dialog_comment.id.values]
    
    dialog_title = author_title[author_title.id.isin(title_id2)]
    dialog_title.reset_index(inplace=True, drop=True)
    
    # print(dialog_title)
    info = []    # num_comments, num_participants 
    # print(comments.groupby(['id', 'author']).count())
    # print(comments.groupby(['id']).count().sort_values('subreddit')) 
    
    '''
    mapping title - comment 
    '''
    dialog_title['id'] = dialog_title['id'].apply(lambda x: 't3_' + x)
    dialog_td = dialog_title[['id', 'author', 'text']] 
    dialog_ct = dialog_comment[['id', 'author', 'text']]  
    merged_df = pd.merge(left = dialog_td, right = dialog_ct, how='inner', on='id')
    
    conv = dict() 
    for id in dialog_td.id: 
        conv[id] = merged_df[merged_df.id == id]
        conv[id].reset_index(inplace=True, drop=True)
    
    print(len(conv), len(conv['t3_eu948']))

    print(conv['t3_eu948'])


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)