import pandas as pd 
import argparse 
import os 
from nltk.tokenize import word_tokenize 
from src import RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    reddit_year = list(range(2010, 2020))
    reddit_p = RedditProcessor(args.data_path)
    reddit_df = pd.DataFrame([[0, 0, 0, 0, 0, 0, 0, 0]], columns=['id', 'subreddit', 'author', 'text', 'type', 'time', 'parent_id', 'o_id'])

    for year in reddit_year: 
       reddit_data = pd.read_csv(os.path.join(data_path, 'processed', f'document_{year}.csv'))
       reddit_df = pd.concat([reddit_df, reddit_data]) 

    reddit_df.drop([0], axis=0, inplace=True)
    del reddit_df['Unnamed: 0']

    print(f'중복 처리 전: {len(reddit_df)}')
    reddit_df = reddit_p.drop_duplicates('text', reddit_df)
    print(f'중복 처리 후: {len(reddit_df)}')
    reddit_df.reset_index(inplace=True, drop=True) 
    reddit_df.to_csv(os.path.join(data_path, 'processed', 'aud_doc.csv'), index=False)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data')
    cli_argse = cli_parser.parse_args()
    main(cli_argse)