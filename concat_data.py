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
    reddit_df = pd.DataFrame([[0, 0, 0, 0, 0]], columns=['id', 'subreddit', 'author', 'text', 'type'])
    
    for year in reddit_year: 
       reddit_data = pd.read_csv(os.path.join(data_path, 'processed', f'document2_{year}.csv'))
       reddit_df = pd.concat([reddit_df, reddit_data]) 

    reddit_df.drop([0], axis=0, inplace=True)
    reddit_df.text = reddit_df.text.apply(lambda x: x.replace('/', ' '))
    reddit_df.text = reddit_df.text.apply(lambda x: x.replace('-', ' '))
    reddit_df.reset_index(inplace=True, drop=True) 
    print(len(reddit_df))

    tok_list = [word_tokenize(context) for context in reddit_df.text.values.tolist()]
    reddit_df['tok_len'] = [len(tok) for tok in tok_list]
    # df_describe = reddit_df.describe()
    # reddit_df.to_csv(os.path.join(data_path, 'processed', 'aplsci.csv'), index=False)
    reddit_df.to_csv(os.path.join(data_path, 'processed', 'aud_tok.csv'), index=False)
    tok_q3 = reddit_df['tok_len'].quantile(0.75) 
    tok_q1 = reddit_df['tok_len'].quantile(0.25) 
    tok_iqr = tok_q3 - tok_q1 
    print(tok_q3 + 1.5 * tok_iqr, tok_q1 - 1.5 * tok_iqr)   # tok: 42 (이상치), tok 평균 길이가 42보다 큰 텍스트 삭제 

    idx_list = [idx for idx in range(len(tok_list)) if len(tok_list[idx]) < int(tok_q3 + 1.5 * tok_iqr)]
    reddit_df = reddit_df.loc[idx_list]
    print(f'중복 처리 전: {len(reddit_df)}')
    reddit_df = reddit_p.drop_duplicates('text', reddit_df)
    print(f'중복 처리 후: {len(reddit_df)}')
    reddit_df.reset_index(inplace=True, drop=True)
    # reddit_df.to_csv(os.path.join(data_path, 'processed', 'aplsci_dsm.csv'), index=False)
    reddit_df.to_csv(os.path.join(data_path, 'processed', 'aud_dsm.csv'), index=False)
    

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data')
    cli_argse = cli_parser.parse_args()
    main(cli_argse)